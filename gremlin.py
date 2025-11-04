
import sys
import os
import datetime
from PySide6.QtWidgets import (
    QWidget, QLabel, QSystemTrayIcon, QMenu, QApplication
)
from PySide6.QtCore import Qt, QTimer, QRect, QUrl
from PySide6.QtGui import QIcon, QAction
from PySide6.QtMultimedia import QSoundEffect

import settings
import sprite_manager
from movement_handler import MovementHandler


class GremlinWindow(QWidget):

    def __init__(self):
        super().__init__()

        # --- @! Window Setup ------------------------------------------------------------
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |     # No window decorations
            Qt.WindowType.WindowStaysOnTopHint |    # Always on top
            Qt.WindowType.Tool                      # Don't show in taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedSize(
            settings.Settings.FrameWidth + 215,
            settings.Settings.FrameHeight + 30
        )

        # --- @! Main Sprite Display -----------------------------------------------------
        self.sprite_label = QLabel(self)
        self.sprite_label.setGeometry(
            105, 5, settings.Settings.FrameWidth, settings.Settings.FrameHeight)
        self.sprite_label.setScaledContents(True)

        # --- @! Hotspots ----------------------------------------------------------------
        self.left_hotspot = QWidget(self)
        self.left_hotspot.setGeometry(110, 95, 60, 85)
        self.left_hotspot.mousePressEvent = self.left_hotspot_click

        self.right_hotspot = QWidget(self)
        self.right_hotspot.setGeometry(280, 95, 60, 85)
        self.right_hotspot.mousePressEvent = self.right_hotspot_click

        self.top_hotspot = QWidget(self)
        self.top_hotspot.setGeometry(160, 0, 135, 50)  # (455-135)/2 = 160
        self.top_hotspot.mousePressEvent = self.top_hotspot_click

        # --- @! Sound Player ------------------------------------------------------------
        self.sound_player = QSoundEffect(self)
        self.sound_player.setVolume(0.8)

        # --- @! Timers ------------------------------------------------------------------
        self.master_timer = QTimer(self)
        self.master_timer.timeout.connect(self.animation_tick)

        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.idle_timer_tick)

        self.close_timer = None

        # --- @! Other tools -------------------------------------------------------------
        self.movement_handler = MovementHandler()

        # --- @! Start -------------------------------------------------------------------
        self.setup_tray_icon()
        self.play_sound("intro.wav")
        self.master_timer.start(1000 // settings.Settings.FrameRate)
        self.idle_timer.start(120 * 1000)
        self.drag_pos = None

    # --- @! Animations ------------------------------------------------------------------

    def play_animation(self, sheet, current_frame, frame_count):
        if sheet is None or frame_count == 0:
            return current_frame

        s = settings.Settings
        x = (current_frame % s.SpriteColumn) * s.FrameWidth
        y = (current_frame // s.SpriteColumn) * s.FrameHeight

        # check bounds
        if x + s.FrameWidth > sheet.width() or y + s.FrameHeight > sheet.height():
            print("Warning: Animation frame out of bounds.")
            return (current_frame + 1) % frame_count

        # create the cropped pixmap
        crop_rect = QRect(x, y, s.FrameWidth, s.FrameHeight)
        cropped_pixmap = sheet.copy(crop_rect)
        self.sprite_label.setPixmap(cropped_pixmap)

        return (current_frame + 1) % frame_count

    def animation_tick(self):
        """
        This method is almost ported 1:1 from KurtVelasco's InitializeAnimations.
        I believe he thinks the original version trash. I think this port is trash too.
        """
        s = settings.Settings
        f = settings.FrameCounts
        c = settings.CurrentFrames
        a = settings.AnimationStates

        if a.IsSleeping and not a.IsIntro:
            c.Sleep = self.play_animation(
                sprite_manager.get("sleep"), c.Sleep, f.Sleep)

        if a.IsIntro:
            c.Intro = self.play_animation(
                sprite_manager.get("intro"), c.Intro, f.Intro)
            if c.Intro == 0:
                a.IsIntro = False

        if a.IsDragging:
            if c.Grab == 0:
                self.play_sound("grab.wav")
            c.Grab = self.play_animation(
                sprite_manager.get("grab"), c.Grab, f.Grab)
            a.IsIntro = a.IsClick = a.IsSleeping = False

        if a.IsPat:
            if c.Pat == 0:
                self.play_sound("grab.wav")
            c.Pat = self.play_animation(
                sprite_manager.get("pat"), c.Pat, f.Pat)
            a.IsIntro = a.IsClick = a.IsSleeping = False
            if c.Pat == 0:
                a.IsPat = False

        if a.IsWalking and not a.IsDragging and not a.IsPat and not a.IsSleeping:
            current_pos = self.pos()
            move_x = current_pos.x()
            move_y = current_pos.y()

            if a.IsWalkingLeft:
                c.WalkLeft = self.play_animation(
                    sprite_manager.get("left"), c.WalkLeft, f.Left)
            elif a.IsWalkingRight:
                c.WalkRight = self.play_animation(
                    sprite_manager.get("right"), c.WalkRight, f.Right)
            elif a.IsWalkingUp:
                c.WalkUp = self.play_animation(
                    sprite_manager.get("backward"), c.WalkUp, f.Up)
            elif a.IsWalkingDown:
                c.WalkDown = self.play_animation(
                    sprite_manager.get("forward"), c.WalkDown, f.Down)

            # apply the new position to the window
            dx, dy = self.movement_handler.getVelocity()
            self.move(move_x + dx, move_y + dy)

        if a.IsHover and not a.IsDragging and not a.IsSleeping and not a.IsWalking:
            c.Hover = self.play_animation(
                sprite_manager.get("hover"), c.Hover, f.Hover)
            a.IsPat = False

        if s.Ammo <= 0:
            if c.Reload == 0:
                self.play_sound("reload.wav")
            a.IsFiring_Left = a.IsFiring_Right = False
            c.Reload = self.play_animation(
                sprite_manager.get("reload"), c.Reload, f.Reload)
            if c.Reload == 0:
                s.Ammo = 5

        if a.IsClick:
            c.Click = self.play_animation(
                sprite_manager.get("click"), c.Click, f.Click)
            a.IsIntro = a.IsSleeping = False
            if c.Click == 0:
                a.IsClick = False

        # --- @! The main "Idle" state ---------------------------------------------------
        if (not a.IsSleeping and not a.IsIntro and not a.IsDragging and
            not a.IsWalkIdle and not a.IsClick and not a.IsHover and
            not a.IsFiring_Left and not a.IsFiring_Right and
                s.Ammo > 0 and not a.IsPat and not a.IsWalking):

            c.Idle = self.play_animation(
                sprite_manager.get("idle"), c.Idle, f.Idle)

        if a.IsFiring_Left and s.Ammo > 0:
            if c.LeftFire == 0:
                self.play_sound("fire.wav")
            c.LeftFire = self.play_animation(
                sprite_manager.get("firel"), c.LeftFire, f.LeftFire)
            if c.LeftFire == 0:
                a.IsFiring_Left = False
                s.Ammo -= 1

        if a.IsFiring_Right and s.Ammo > 0:
            if c.RightFire == 0:
                self.play_sound("fire.wav")
            c.RightFire = self.play_animation(
                sprite_manager.get("firer"), c.RightFire, f.RightFire
            )
            if c.RightFire == 0:
                a.IsFiring_Right = False
                s.Ammo -= 1

    def play_sound(self, file_name, delay_seconds=0):
        """ Plays a sound, respecting the LastPlayed delay. """
        path = os.path.join(
            settings.BASE_DIR, "Sounds", settings.Settings.StartingChar, file_name)
        if not os.path.exists(path):
            return

        if delay_seconds > 0:
            last_time = settings.Settings.LastPlayed.get(file_name)
            if last_time:
                if (datetime.datetime.now() - last_time).total_seconds() < delay_seconds:
                    return

        try:
            self.sound_player.setSource(QUrl.fromLocalFile(path))
            self.sound_player.play()
            settings.Settings.LastPlayed[file_name] = datetime.datetime.now()
        except Exception as e:
            print(f"Sound error: {e}")

    # --- @! System Tray and App Lifecycle ---------------------------------------------------------

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)

        icon_path = os.path.join(settings.BASE_DIR, "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(settings.BASE_DIR, "icon.png")

        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(QIcon.fromTheme("applications-games"))

        self.tray_icon.setToolTip("Gremlin")

        menu = QMenu()
        menu.addSeparator()

        reappear_action = QAction("Reappear", self)
        reappear_action.triggered.connect(self.reset_app)
        menu.addAction(reappear_action)

        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close_app)
        menu.addAction(close_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def reset_app(self):
        self.tray_icon.hide()
        QApplication.quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def close_app(self):
        self.master_timer.stop()
        self.idle_timer.stop()
        self.tray_icon.hide()

        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.outro_tick)
        self.close_timer.start(1000 // settings.Settings.FrameRate)

    def outro_tick(self):
        s = settings
        s.CurrentFrames.Outro = self.play_animation(
            sprite_manager.get("outro"),
            s.CurrentFrames.Outro,
            s.FrameCounts.Outro
        )

        if s.CurrentFrames.Outro == 0:
            self.close_timer.stop()
            QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.close_app()

    # --- @! Event Handlers (Mouse) ------------------------------------------------------

    def reset_idle_timer(self):
        self.idle_timer.start(120 * 1000)
        settings.AnimationStates.IsSleeping = False

    def idle_timer_tick(self):
        if not settings.AnimationStates.IsSleeping:
            settings.AnimationStates.IsSleeping = True

    def mousePressEvent(self, event):
        """ Handles clicks on the main window (Grid in XAML). """
        self.reset_idle_timer()
        if event.button() == Qt.MouseButton.LeftButton:
            settings.AnimationStates.IsDragging = True
            settings.CurrentFrames.Grab = 0
            self.drag_pos = event.globalPosition().toPoint() - self.pos()

        elif event.button() == Qt.MouseButton.RightButton:
            s = settings
            s.CurrentFrames.Click = 0
            s.AnimationStates.IsClick = not s.AnimationStates.IsClick
            if s.AnimationStates.IsClick:
                self.play_sound("mambo.wav")

    def mouseMoveEvent(self, event):
        """ Handles dragging the window. """
        if (settings.AnimationStates.IsDragging and
                event.buttons() == Qt.MouseButton.LeftButton):
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        """ Handles dropping the window. """
        if event.button() == Qt.MouseButton.LeftButton:
            settings.AnimationStates.IsDragging = False
            settings.CurrentFrames.Grab = 0
            self.play_sound("run.wav")

    def keyPressEvent(self, event):
        """ Handles keyboard controls when window is focused (on hover). """
        if event.isAutoRepeat():
            return

        # only start walking if not in a conflicting state
        a = settings.AnimationStates
        if a.IsDragging or a.IsPat or a.IsSleeping or a.IsClick:
            return

        prev_walking = a.IsWalking
        self.movement_handler.recordKeyPress(event)
        self.movement_handler.transferAnimationState(a)

        if a.IsWalking:
            if not prev_walking:
                self.play_sound("run.wav")
            self.reset_idle_timer()

    def keyReleaseEvent(self, event):
        """ Handles key releases to stop walking. """
        if event.isAutoRepeat():
            return

        a = settings.AnimationStates
        self.movement_handler.recordKeyRelease(event)
        self.movement_handler.transferAnimationState(a)

        if not a.IsWalking:
            c = settings.CurrentFrames
            c.WalkUp = c.WalkDown = c.WalkLeft = c.WalkRight = 0
            # re-enable hover animation if mouse is still over
            if self.underMouse():
                a.IsHover = True

    def enterEvent(self, event):
        """ Handles mouse enter event. """
        self.setFocus()
        a = settings.AnimationStates
        if not a.IsIntro and not a.IsWalking:
            a.IsHover = True
        if not a.IsIntro and not a.IsWalking and not a.IsSleeping and not a.IsClick:
            self.play_sound("hover.wav", 3)

    def leaveEvent(self, event):
        """ Handles mouse leave event. """
        self.clearFocus()
        a = settings.AnimationStates
        if not settings.AnimationStates.IsIntro:
            a.IsHover = False
            settings.CurrentFrames.Hover = 0
        self.movement_handler.recordMouseLeave()
        self.movement_handler.transferAnimationState(a)

    # --- @! Hotspot Click Handlers ------------------------------------------------------

    def left_hotspot_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.reset_idle_timer()
            settings.AnimationStates.IsFiring_Left = True

    def right_hotspot_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.reset_idle_timer()
            settings.AnimationStates.IsFiring_Right = True

    def top_hotspot_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.reset_idle_timer()
            settings.CurrentFrames.Pat = 0
            settings.AnimationStates.IsPat = True
