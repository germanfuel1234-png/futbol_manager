"""
Servicio de partidos: CRUD de partidos y gestión de jugadores.
"""
from datetime import datetime
from src.models import Match, MatchPlayer, MatchType, MatchStatus, PaymentStatus, User, get_session
from src.services.auth_service import get_current_user


def create_match(title: str, match_type: str, match_date: datetime,
                  venue: str, total_cost: float, notes: str = "") -> tuple[bool, object | str]:
    """Crea un partido. Retorna (éxito, match | mensaje_error)."""
    user = get_current_user()
    if not user:
        return False, "not_authenticated"

    session = get_session()
    try:
        match = Match(
            title=title.strip(),
            match_type=MatchType(match_type),
            match_date=match_date,
            venue=venue.strip(),
            total_cost=float(total_cost),
            notes=notes.strip(),
            organizer_id=user.id,
            status=MatchStatus.PENDING,
        )
        session.add(match)
        session.flush()

        # Agregar al organizador como jugador confirmado
        mp = MatchPlayer(match_id=match.id, player_id=user.id, confirmed=True)
        session.add(mp)
        session.commit()
        session.refresh(match)
        match_id = match.id
        session.expunge_all()
        return True, match_id
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def get_all_matches() -> list[dict]:
    """Retorna todos los partidos con datos básicos para el dashboard."""
    session = get_session()
    try:
        matches = session.query(Match).order_by(Match.match_date.desc()).all()
        result = []
        for m in matches:
            organizer = session.query(User).filter_by(id=m.organizer_id).first()
            result.append({
                "id": m.id,
                "title": m.title,
                "match_type": m.match_type.value,
                "match_date": m.match_date,
                "venue": m.venue,
                "total_cost": m.total_cost,
                "status": m.status.value,
                "max_players": m.max_players,
                "confirmed_count": m.confirmed_players_count,
                "available_spots": m.available_spots,
                "cost_per_player": m.cost_per_player,
                "organizer_name": organizer.name if organizer else "—",
                "organizer_id": m.organizer_id,
            })
        return result
    finally:
        session.close()


def get_match_detail(match_id: int) -> dict | None:
    """Retorna detalles completos del partido incluyendo jugadores."""
    session = get_session()
    try:
        match = session.query(Match).filter_by(id=match_id).first()
        if not match:
            return None

        organizer = session.query(User).filter_by(id=match.organizer_id).first()
        players_data = []
        for mp in match.players:
            player = session.query(User).filter_by(id=mp.player_id).first()
            if player:
                players_data.append({
                    "mp_id": mp.id,
                    "player_id": player.id,
                    "player_name": player.name,
                    "player_position": player.position,
                    "confirmed": mp.confirmed,
                    "payment_status": mp.payment_status.value,
                    "amount_due": mp.amount_due,
                    "goals": mp.goals,
                    "assists": mp.assists,
                    "yellow_cards": mp.yellow_cards,
                    "red_cards": mp.red_cards,
                    "is_mvp": mp.is_mvp,
                })

        return {
            "id": match.id,
            "title": match.title,
            "match_type": match.match_type.value,
            "match_date": match.match_date,
            "venue": match.venue,
            "total_cost": match.total_cost,
            "status": match.status.value,
            "notes": match.notes or "",
            "max_players": match.max_players,
            "confirmed_count": match.confirmed_players_count,
            "available_spots": match.available_spots,
            "cost_per_player": match.cost_per_player,
            "organizer_id": match.organizer_id,
            "organizer_name": organizer.name if organizer else "—",
            "players": players_data,
        }
    finally:
        session.close()


def add_player_to_match(match_id: int, player_email: str) -> tuple[bool, str]:
    """Agrega un jugador al partido por email."""
    session = get_session()
    try:
        player = session.query(User).filter_by(email=player_email.lower().strip()).first()
        if not player:
            return False, "user_not_found"

        existing = session.query(MatchPlayer).filter_by(
            match_id=match_id, player_id=player.id
        ).first()
        if existing:
            return False, "already_in_match"

        match = session.query(Match).filter_by(id=match_id).first()
        if not match:
            return False, "match_not_found"
        if match.available_spots <= 0:
            return False, "match_full"

        mp = MatchPlayer(match_id=match_id, player_id=player.id, confirmed=True,
                         amount_due=match.cost_per_player)
        session.add(mp)
        session.commit()
        return True, player.name
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()


def update_payment_status(mp_id: int, status: str) -> bool:
    """Actualiza el estado de pago de un jugador en un partido."""
    session = get_session()
    try:
        mp = session.query(MatchPlayer).filter_by(id=mp_id).first()
        if not mp:
            return False
        mp.payment_status = PaymentStatus(status)
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def update_match_status(match_id: int, status: str) -> bool:
    session = get_session()
    try:
        match = session.query(Match).filter_by(id=match_id).first()
        if not match:
            return False
        match.status = MatchStatus(status)
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def save_match_stats(match_id: int, stats: list[dict]) -> bool:
    """
    stats: lista de dicts con keys:
      mp_id, goals, assists, yellow_cards, red_cards, is_mvp
    """
    session = get_session()
    try:
        for s in stats:
            mp = session.query(MatchPlayer).filter_by(id=s["mp_id"]).first()
            if mp:
                mp.goals = int(s.get("goals", 0))
                mp.assists = int(s.get("assists", 0))
                mp.yellow_cards = int(s.get("yellow_cards", 0))
                mp.red_cards = int(s.get("red_cards", 0))
                mp.is_mvp = bool(s.get("is_mvp", False))
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def delete_match(match_id: int) -> bool:
    session = get_session()
    try:
        match = session.query(Match).filter_by(id=match_id).first()
        if match:
            session.delete(match)
            session.commit()
            return True
        return False
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def get_user_stats(user_id: int) -> dict:
    """Estadísticas acumuladas de un jugador."""
    session = get_session()
    try:
        mps = session.query(MatchPlayer).filter_by(player_id=user_id).all()
        return {
            "total_matches": len(mps),
            "total_goals": sum(mp.goals for mp in mps),
            "total_assists": sum(mp.assists for mp in mps),
            "yellow_cards": sum(mp.yellow_cards for mp in mps),
            "red_cards": sum(mp.red_cards for mp in mps),
            "mvp_count": sum(1 for mp in mps if mp.is_mvp),
        }
    finally:
        session.close()
