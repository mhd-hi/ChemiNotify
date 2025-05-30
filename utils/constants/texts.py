WINDOW_TITLES = {
    'LOGIN_TITLE_BAR': ['Bienvenue sur ChemiNot']    
}
UNWANTED_WINDOW_TITLES = ['cheminot', 'à propos de ', 'Attention']
EXEMPTED_WINDOW_TITLES = ['Visual Studio Code', 'visual studio code', 'vs code', 'ChemiNotify - Visual Studio Code']  # needed to code this app lol

# Empty text means match any text
# Empty list means match any title

POPUP_COURSE_FULL = {
    'title': [],
    'text': ['cours est complet'],
    'return_value': 'course_full'
}

POPUP_SCHEDULE_CONFLICT = {
    'title': [],
    'text': ['conflit d\'horaire', 'conflit d'],
    'return_value': 'schedule_conflict'
}

POPUP_ERROR = {
    'title': [],
    'text': ['erreur'],
    'return_value': 'erreur'
}

POPUP_ABOUT = {
    'title': ['À propos de ChemiNot'],
    'text': [],
    'return_value': 'about'
}

POPUP_SESSION_SELECTION = {
    'title': ['ChemiNot'],
    'text': ['Pour quelle session voulez-vous'], # Pour quelle session voulez-vous modifier votre choix de cours ?
    'return_value': 'session_selection',
    'action': 'alt_f4'
}

POPUP_ATTENTION = {
    'title': ['ATTENTION'],
    'text': ['est obligatoire si'], # 'Le cours PEP110 est obligatoire si vous devez suivre TIN503',
    'return_value': 'attention',
    'action': 'alt_f4'
}

POPUP_TYPES = [
    POPUP_COURSE_FULL,
    POPUP_SCHEDULE_CONFLICT,
    POPUP_ERROR,
    POPUP_ABOUT,
    POPUP_SESSION_SELECTION,
    POPUP_ATTENTION
]

# Default return value for unknown popups
POPUP_UNKNOWN_RETURN_VALUE = 'unknown'