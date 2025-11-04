
from PySide6.QtCore import Qt
import settings


class MovementHandler:
    def __init__(self):
        self.w = False
        self.a = False
        self.s = False
        self.d = False
        self.v = settings.Settings.MoveSpeed

    def getVelocity(self) -> tuple[int, int]:
        """
        Returns the velocity vector based on the current key states.
        If both keys in a direction are pressed, they cancel each other out.
        """
        vy = 0
        vx = 0
        if self.w ^ self.s:
            vy = -self.v if self.w else self.v
        if self.a ^ self.d:
            vx = -self.v if self.a else self.v
        return vx, vy

    def transferAnimationState(self, a: settings.AnimationStates) -> None:
        """
        Unlike `getVelocity` where the movement can be diagonal, there's no diagonal
        animation. So we prioritize vertical movement over horizontal movement.
        """
        a.IsWalkingUp = a.IsWalkingDown = a.IsWalkingLeft = a.IsWalkingRight = False

        if self.w ^ self.s:
            if self.w:
                a.IsWalkingUp = True
            else:
                a.IsWalkingDown = True
        elif self.a ^ self.d:
            if self.a:
                a.IsWalkingLeft = True
            else:
                a.IsWalkingRight = True

        if a.IsWalkingUp or a.IsWalkingDown or a.IsWalkingLeft or a.IsWalkingRight:
            a.IsWalking = True
            a.IsHover = a.IsPat = a.IsClick = a.IsSleeping = a.IsIntro = False
        else:
            a.IsWalking = False

    # --- @! event recorders -------------------------------------------------------------

    def recordKeyPress(self, event):
        key = event.key()
        match key:
            case Qt.Key.Key_W:
                self.w = True
            case Qt.Key.Key_A:
                self.a = True
            case Qt.Key.Key_S:
                self.s = True
            case Qt.Key.Key_D:
                self.d = True
            case _:
                pass

    def recordKeyRelease(self, event):
        key = event.key()
        match key:
            case Qt.Key.Key_W:
                self.w = False
            case Qt.Key.Key_A:
                self.a = False
            case Qt.Key.Key_S:
                self.s = False
            case Qt.Key.Key_D:
                self.d = False
            case _:
                pass

    def recordMouseLeave(self):
        self.w = False
        self.a = False
        self.s = False
        self.d = False
