"""Fitness calculation for training."""

from neurotraffic.core.config import Config


def calculate_fitness(metrics):
    """Calculate fitness score from collected metrics.

    Rewards completed cars with short trips.
    Penalizes waiting, congestion, stuck cars, and excessive light switching.
    """
    return (
        metrics.cars_completed * Config.FIT_CARS_COMPLETED
        + metrics.average_travel_time * Config.FIT_AVG_TRAVEL_TIME
        + metrics.average_wait_time * Config.FIT_AVG_WAIT_TIME
        + metrics.congestion_score * Config.FIT_CONGESTION
        + metrics.light_switch_count * Config.FIT_LIGHT_SWITCHES
        + metrics.active_cars_at_end * Config.FIT_STUCK_CARS
        + metrics.avg_active_wait * Config.FIT_ACTIVE_WAIT
    )
