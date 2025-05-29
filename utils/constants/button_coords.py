REF_WINDOW_SIZES = {
    "LOGIN":        (364.0, 321.0),
    "LE_CHEMINOT":  (608.0, 468.0),
}

LOGIN_STATE_COORDS = {
    'USERNAME_FIELD': (180, 19),
    'PASSWORD_FIELD': (184, 47),
    'LOGIN_BUTTON': (314, 45),  
}

TABS = {
    'INSCRIPTION_SESSION': (230, 6),
    'SELECTION_COURS': (63, 27),
    'HORAIRE': (167, 27),
    'QUITTER': (549, 5),
}

COURSE_SELECTION_COORDS = {
    'MAT145': (40, 95),
    'ING150': (40,136),
    'ATE100': (40,193),
    'ATE150': (40,221),
    'LOG100': (40,263),
    'CHM131': (40,304),
    'PRE013': (40,332),
    
    'ATE075': (135,397),
    'ATE085': (209,397),
    'INF111': (281,397),
    'MAT144': (135,410),
    'PHY144': (214,410),
    'LRC105': (278,410),
    
    'MAT210': (120,178),
    'LOG121': (120,248),
    
    'MAT265': (197,121),
    'PHY332': (197,150),
    'ING160': (197,166),
    'LOG210': (197,249),
    'LOG240': (197,305),
    
    'MAT472': (270,107),
    'PHY335': (270,136),
    'LOG320': (270,193),
    'GTI350': (270,221),
    'COM410': (270,263),
    'LOG410': (270,304),
    'LOG515': (270,318),
    'LOG510': (270,333),
    'PEP110': (270,347),
    
    'MAT350': (350,94),
    'GTI650': (350,136),
    'LOG675': (350,222),
    'LOG430': (350,249),
    
    # Cours choix
    'GIA602': (430,127),
    'GPE450': (430,141),
    'GPO602': (430,153),
    'ENT201': (430,169),
    'ENT202': (430,184),
    'ENT601': (430,197),
    'ING500': (430,210),
    'LRC110': (430,224),
    'ETH610': (430,241),
    # End cours choix
    
    'GTI755': (430,136),
    'GTI750': (430,165),
    'LOG660': (430,193),
    'GTI611': (430,278),
    'GIA400': (430,347),
    
    'LOG450': (505, 96),
    'LOG460': (505,110),
    'LOG530': (505,124),
    'LOG550': (505,138),
    'LOG635': (505,151),
    'LOG645': (505,166),
    'LOG680': (505,178),
    'LOG710': (505,193),
    'LOG721': (505,205),
    'LOG725': (505,224),
    'LOG736': (505,235),
    'LOG750': (505,249),
    'LOG780': (505,263),
    'LOG619': (505,292),
    'TIN503': (505,319),
    'GTI320': (505,347),
    
    'GTI525': (580,108),
    'GTI700': (580,137),
    'GTI719': (580,152),
    'GTI720': (580,165),
    'GTI771': (580,179),
    'GTI723': (580,195),
    'GTI745': (580,207),
    'GTI780': (580,221),
    'ELE543': (580,236),
    'ELE641': (580,250),
    'ELE674': (580,265),
    'LOG791': (580,290),
    'LOG795': (580,306),
}

# X coordinates, day columns
MONDAY_X = 113
TUESDAY_X = 201
WEDNESDAY_X = 300
THURSDAY_X = 391
FRIDAY_X = 378
SATURDAY_X = 571

# Y coordinates, Time rows
AM_Y = 209
PM_Y = 292 
EV_Y = 367

HORAIRE_STATE_COORDS = {
    'GROUP_COURSE_BLACK_PIXEL': (348, 67),
    
    'MONDAY_AM': (MONDAY_X, AM_Y),
    'MONDAY_PM': (MONDAY_X, PM_Y),
    'MONDAY_EV': (MONDAY_X, EV_Y),
    
    'TUESDAY_AM': (TUESDAY_X, AM_Y),
    'TUESDAY_PM': (TUESDAY_X, PM_Y),
    'TUESDAY_EV': (TUESDAY_X, EV_Y),
    
    'WEDNESDAY_AM': (WEDNESDAY_X, AM_Y),
    'WEDNESDAY_PM': (WEDNESDAY_X, PM_Y),
    'WEDNESDAY_EV': (WEDNESDAY_X, EV_Y),
    
    'THURSDAY_AM': (THURSDAY_X, AM_Y),
    'THURSDAY_PM': (THURSDAY_X, PM_Y),
    'THURSDAY_EV': (THURSDAY_X, EV_Y),
    
    'FRIDAY_AM': (FRIDAY_X, AM_Y),
    'FRIDAY_PM': (FRIDAY_X, PM_Y),
    'FRIDAY_EV': (FRIDAY_X, EV_Y),
    
    'SATURDAY_AM': (SATURDAY_X, AM_Y),
    'SATURDAY_PM': (SATURDAY_X, PM_Y),
    'SATURDAY_EV': (SATURDAY_X, EV_Y),
}