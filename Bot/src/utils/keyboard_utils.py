"""
Keyboard Utilities Module
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List

def create_main_keyboard() -> InlineKeyboardMarkup:
    """Create the main menu inline keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("Services", switch_inline_query_current_chat=""),
            InlineKeyboardButton("Balance", callback_data="balance")
        ],
        [
            InlineKeyboardButton("Recharge", callback_data="recharge"),
            InlineKeyboardButton("Use Promocode", callback_data="promocode")
        ],
        # Removed search button - using only callback-based approach
        [
            InlineKeyboardButton("Profile", callback_data="profile"),
            InlineKeyboardButton("Support", callback_data="support")
        ],
        [
            InlineKeyboardButton("History", callback_data="history")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def create_back_keyboard() -> InlineKeyboardMarkup:
    """Create a back button keyboard"""
    keyboard = [
        [InlineKeyboardButton("« Back", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_services_keyboard(services: List[dict]) -> InlineKeyboardMarkup:
    """Create services keyboard (placeholder for future implementation)"""
    keyboard = []
    
    # Add service buttons (placeholder)
    for i, service in enumerate(services[:6]):  # Limit to 6 services
        keyboard.append([
            InlineKeyboardButton(
                f"{service.get('name', 'Service')} - ₹{service.get('price', '0')}", 
                callback_data=f"service_{service.get('id', i)}"
            )
        ])
    
    # Add back button
    keyboard.append([InlineKeyboardButton("« Back", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(keyboard)

def create_balance_keyboard() -> InlineKeyboardMarkup:
    """Create balance overview keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("Recharge", callback_data="recharge"),
            InlineKeyboardButton("💎 Transactions", callback_data="transactions")
        ],
        [
            InlineKeyboardButton("« Back", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_transactions_keyboard() -> InlineKeyboardMarkup:
    """Create transactions keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("« Back", callback_data="balance")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_payment_keyboard() -> InlineKeyboardMarkup:
    """Create payment options keyboard (placeholder)"""
    keyboard = [
        [
            InlineKeyboardButton("UPI Payment", callback_data="payment_upi"),
            InlineKeyboardButton("Card Payment", callback_data="payment_card")
        ],
        [
            InlineKeyboardButton("Crypto Payment", callback_data="payment_crypto")
        ],
        [
            InlineKeyboardButton("« Back", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
