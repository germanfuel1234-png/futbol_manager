"""
Modelos de base de datos con SQLAlchemy (SQLite local).
Diseñado para migrar fácilmente a Supabase/PostgreSQL.
"""
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    Boolean, DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
import enum
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "futbol_manager.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


# ─── Enums ────────────────────────────────────────────────────────────────────

class MatchType(str, enum.Enum):
    FUTSAL = "futsal"
    FOOTBALL7 = "football7"
    FOOTBALL11 = "football11"


class MatchStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CONFIRMED = "confirmed"


class PlayerPosition(str, enum.Enum):
    GOALKEEPER = "Arquero"
    DEFENDER = "Defensor"
    MIDFIELDER = "Mediocampista"
    FORWARD = "Delantero"
    ANY = "Cualquiera"


# ─── Modelos ──────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    phone = Column(String(30), nullable=True)
    position = Column(String(50), default=PlayerPosition.ANY)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    organized_matches = relationship("Match", back_populates="organizer", foreign_keys="Match.organizer_id")
    match_participations = relationship("MatchPlayer", back_populates="player")

    @property
    def total_goals(self):
        return sum(p.goals for p in self.match_participations)

    @property
    def total_assists(self):
        return sum(p.assists for p in self.match_participations)

    @property
    def total_matches(self):
        return len(self.match_participations)


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    logo_url = Column(String(500), nullable=True)
    captain_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    captain = relationship("User", foreign_keys=[captain_id])
    matches_home = relationship("Match", back_populates="home_team", foreign_keys="Match.home_team_id")
    matches_away = relationship("Match", back_populates="away_team", foreign_keys="Match.away_team_id")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    match_type = Column(SAEnum(MatchType), nullable=False)
    match_date = Column(DateTime, nullable=False)
    venue = Column(String(300), nullable=True)
    total_cost = Column(Float, default=0.0)
    status = Column(SAEnum(MatchStatus), default=MatchStatus.PENDING)
    notes = Column(String(1000), nullable=True)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organizer = relationship("User", back_populates="organized_matches", foreign_keys=[organizer_id])
    home_team = relationship("Team", back_populates="matches_home", foreign_keys=[home_team_id])
    away_team = relationship("Team", back_populates="matches_away", foreign_keys=[away_team_id])
    players = relationship("MatchPlayer", back_populates="match", cascade="all, delete-orphan")

    @property
    def max_players(self):
        return {MatchType.FUTSAL: 10, MatchType.FOOTBALL7: 14, MatchType.FOOTBALL11: 22}[self.match_type]

    @property
    def confirmed_players_count(self):
        return len([p for p in self.players if p.confirmed])

    @property
    def cost_per_player(self):
        count = self.confirmed_players_count
        return round(self.total_cost / count, 2) if count > 0 else 0.0

    @property
    def available_spots(self):
        return max(0, self.max_players - self.confirmed_players_count)


class MatchPlayer(Base):
    """Tabla pivote: jugador en un partido específico."""
    __tablename__ = "match_players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    confirmed = Column(Boolean, default=False)
    payment_status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    amount_due = Column(Float, default=0.0)
    # Estadísticas del partido
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    is_mvp = Column(Boolean, default=False)

    match = relationship("Match", back_populates="players")
    player = relationship("User", back_populates="match_participations")


def init_db():
    """Crear todas las tablas si no existen."""
    Base.metadata.create_all(engine)


def get_session():
    """Context manager para sesiones de BD."""
    return SessionLocal()
