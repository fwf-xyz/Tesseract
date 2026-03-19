from aiogram import Router, types
from aiogram.filters import Command

from utils import send_main_menu
from keyboards import get_main_reply_keyboard
from middlewares import Repository


router = Router()