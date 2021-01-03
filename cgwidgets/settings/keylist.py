from qtpy.QtCore import Qt

CHARACTER_KEYS = [
    Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D,
    Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H,
    Qt.Key_I, Qt.Key_J, Qt.Key_K, Qt.Key_L,
    Qt.Key_M, Qt.Key_N, Qt.Key_O, Qt.Key_P,
    Qt.Key_Q, Qt.Key_R, Qt.Key_S, Qt.Key_T,
    Qt.Key_U, Qt.Key_V, Qt.Key_W, Qt.Key_X,
    Qt.Key_Y, Qt.Key_Z
]

NUMBER_KEYS = [
    Qt.Key_0, Qt.Key_1, Qt.Key_2,
    Qt.Key_3, Qt.Key_4, Qt.Key_5,
    Qt.Key_6, Qt.Key_7, Qt.Key_8,
    Qt.Key_9,
]

ARROW_KEYS = [
    Qt.Key_Left,
    Qt.Key_Right,
    Qt.Key_Up,
    Qt.Key_Down,
]

HOME_KEYS = [
    Qt.Key_Delete,
    Qt.Key_Backspace,
    Qt.Key_Return,
    Qt.Key_Enter,
    Qt.Key_CapsLock
]

MATH_KEYS = [
    Qt.Key_Plus,
    Qt.Key_plusminus,
    Qt.Key_Minus,
    Qt.Key_multiply,
    Qt.Key_Asterisk,
    Qt.Key_Slash
]

NUMERICAL_INPUT_KEYS = (
    NUMBER_KEYS
    + ARROW_KEYS
    + HOME_KEYS
)

def booleanKeyList(base_keylist, keylist_to_remove):
    """
    Removes one keylist from another

    Args:
        base_keylist (attrs.KEY_LIST): keylist to remove items from
        keylist_to_remove(attrs.KEY_LIST): keylist of items to be removed from
            the base_keylist
    """
    new_keylist = [item for item in base_keylist if item not in keylist_to_remove]
    return new_keylist


# a = booleanKeyList(CHARACTER_KEYS, [Qt.Key_A, Qt.Key_B])
# print(len(a))
