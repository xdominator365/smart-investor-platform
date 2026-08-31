import os
import requests
import numpy as np
from datetime import datetime, timedelta
from textblob import TextBlob

from models.news_event import NewsEvent


class NewsService:
    """
    News Intelligence Service
    - Fetches real-time financial news
    - Computes sentiment
    - Stores news events
    - Aggregates insights for ML & UI
    """

    BASE_URL = "https://api.marketaux.com/v1/news/all"
    API_KEY = os.getenv("MARKETAUX_API_KEY")

    # ---------------------------
    # Internal helpers
    # ---------------------------

    @staticmethod
    def _require_api_key():
        if not NewsService.API_KEY:
            raise RuntimeError(
                "MARKETAUX_API_KEY not set. "
                "Export it as an environment variable."
            )

    @staticmethod
    def _compute_sentiment(text: str):
        if not text:
            return 0.0, 0.0
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # [-1, 1]
        confidence = abs(polarity)
        return polarity, confidence

    @staticmethod
    def _sentiment_label(score: float):
        if score > 0.2:
            return "POSITIVE"
        if score < -0.2:
            return "NEGATIVE"
        return "NEUTRAL"

    @staticmethod
    def _attention_label(volume: int):
        if volume >= 20:
            return "VERY_HIGH"
        if volume >= 10:
            return "HIGH"
        if volume >= 3:
            return "MODERATE"
        return "LOW"

    # ---------------------------
    # Fetch raw news (GLOBAL)
    # ---------------------------

    @staticmethod
    def fetch_news(symbol: str, country: str | None = None):
        """
        Fetch raw news articles for a symbol.
        Country is optional (global by default).
        """
        NewsService._require_api_key()

        params = {
            "symbols": symbol,
            "language": "en",
            "api_token": NewsService.API_KEY,
            "limit": 50,
            "filter_entities": "true"
        }

        if country:
            params["countries"] = country

        response = requests.get(NewsService.BASE_URL, params=params)
        response.raise_for_status()

        return response.json().get("data", [])

    # ---------------------------
    # Ingest & persist news
    # ---------------------------

    @staticmethod
    def ingest_news(db, symbol: str, country: str | None = None):
        """
        Fetches latest news and stores it in DB.
        Safe to call multiple times.
        """
        articles = NewsService.fetch_news(symbol, country)

        if not articles:
            return {"status": "NO_NEWS", "message": "No articles returned"}

        for a in articles:
            text = f"{a.get('title','')} {a.get('description','')}"
            sentiment, confidence = NewsService._compute_sentiment(text)

            event = NewsEvent(
                symbol=symbol.upper(),
                headline=a.get("title"),
                sentiment_score=sentiment,
                confidence_score=confidence,
                source=a.get("source"),
                url=a.get("url"),
                event_time=datetime.fromisoformat(
                    a["published_at"].replace("Z", "")
                )
            )

            db.add(event)

        db.commit()

        return {
            "status": "INGESTED",
            "articles_saved": len(articles)
        }

    # ---------------------------
    # Aggregate sentiment
    # ---------------------------

    @staticmethod
    def aggregate_sentiment(db, symbol: str):
        """
        Aggregates sentiment over rolling windows.
        Returns NO_DATA if nothing exists.
        """
        now = datetime.utcnow()

        def fetch(hours):
            return (
                db.query(NewsEvent)
                .filter(
                    NewsEvent.symbol == symbol.upper(),
                    NewsEvent.event_time >= now - timedelta(hours=hours)
                )
                .all()
            )

        news_24h = fetch(24)
        news_7d = fetch(24 * 7)
        
        latest_event_time = None
        all_news = news_24h + news_7d

        if all_news:
            latest_event_time = max(n.event_time for n in all_news)

        if not news_24h and not news_7d:
            return {
                "status": "NO_DATA",
                "message": "No news ingested yet for this symbol"
            }

        def avg(news):
            return float(np.mean([n.sentiment_score for n in news])) if news else 0.0

        avg_24h = avg(news_24h)
        avg_7d = avg(news_7d)

        return {
            "status": "OK",
            "avg_sentiment_24h": avg_24h,
            "avg_sentiment_7d": avg_7d,
            "sentiment_trend": avg_24h - avg_7d,
            "news_volume_24h": len(news_24h),
            "news_volume_7d": len(news_7d),
            "last_updated_at": latest_event_time.isoformat() if latest_event_time else None
        }

    # ---------------------------
    # Build insight (UI / ML)
    # ---------------------------

    @staticmethod
    def build_insight(db, symbol: str):
        """
        High-level interpretation for humans & ML.
        """
        
        # Auto-ingest on first request or stale data
        NewsService.ensure_news_ingested(db, symbol)
        
        data = NewsService.aggregate_sentiment(db, symbol)

        if data["status"] != "OK":
            return data

        trend = (
            "IMPROVING"
            if data["sentiment_trend"] > 0
            else "WEAKENING"
        )

        risk_flags = []
        if data["avg_sentiment_24h"] < -0.6:
            risk_flags.append("NEGATIVE_NEWS_SPIKE")

        return {
            "symbol": symbol.upper(),
            "market_scope": "GLOBAL",
            "last_updated_at": data.get("last_updated_at"),
            "sentiment": {
                "avg_24h": round(data["avg_sentiment_24h"], 3),
                "avg_7d": round(data["avg_sentiment_7d"], 3),
                "trend": trend,
                "label": NewsService._sentiment_label(
                    data["avg_sentiment_24h"]
                )
            },
            "attention": {
                "articles_24h": data["news_volume_24h"],
                "articles_7d": data["news_volume_7d"],
                "attention_level": NewsService._attention_label(
                    data["news_volume_24h"]
                )
            },
            "risk_flags": risk_flags,
            "summary": (
                f"{trend.capitalize()} sentiment with "
                f"{NewsService._attention_label(data['news_volume_24h']).lower()} attention"
            )
        }

    # ---------------------------
    # Apply news overlay to ML
    # ---------------------------

    @staticmethod
    def apply_news_overlay(base_score: float, insight: dict):
        """
        Adjust ML ranking score safely using news.
        """
        if insight.get("sentiment") is None:
            return base_score, 0.0, None

        sentiment_score = (
            0.6 * insight["sentiment"]["avg_24h"] +
            0.4 * insight["sentiment"]["avg_7d"]
        )

        boost = np.clip(sentiment_score * 0.15, -0.15, 0.15)
        final_score = base_score * (1 + boost)

        risk = None
        if "NEGATIVE_NEWS_SPIKE" in insight["risk_flags"]:
            final_score *= 0.7
            risk = "NEGATIVE_NEWS_SPIKE"

        return final_score, boost, risk
    
    @staticmethod
    def _is_news_stale(db, symbol: str, ttl_minutes: int = 60) -> bool:
        """
        Returns True if no news exists or latest news is older than TTL.
        """
        latest = (
            db.query(NewsEvent)
            .filter(NewsEvent.symbol == symbol.upper())
            .order_by(NewsEvent.event_time.desc())
            .first()
        )

        if not latest:
            return True

        age = datetime.utcnow() - latest.event_time
        return age > timedelta(minutes=ttl_minutes)
    
    @staticmethod
    def ensure_news_ingested(db, symbol: str, country: str | None = None):
        """
        Ensures news exists in DB for a symbol.
        Ingests only if missing or stale.
        """
        if NewsService._is_news_stale(db, symbol):
            print(f"[NEWS] Ingesting fresh news for {symbol}")
            NewsService.ingest_news(db, symbol, country)
        else:
            print(f"[NEWS] Using cached news for {symbol}")
