from .xo import router as xo_router
from .word_games import router as word_router
from .number_games import router as number_router
from .card_games import router as card_router
from .dice_games import router as dice_router

ALL_ROUTERS = [
    xo_router,
    word_router,
    number_router,
    card_router,
    dice_router,
]
