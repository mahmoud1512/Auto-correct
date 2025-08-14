# import minimum_edit_distance
# # autocorrect_ui.py
# """
# PyQt5 UI for autocorrect suggestions.

# Requirements:
#     pip install PyQt5

# Behavior:
#     - Type a word in the input field and press Enter or click 'Suggest'.
#     - The app calls:
#         get_the_nearest_string(word, WORDLIST_PATH)
#       which must return a list (top suggestions).
#     - Suggestions (up to 5) are shown in the list. Double-click a suggestion to fill the input.
# """

# import sys
# import traceback
# from typing import List

# from PyQt5 import QtCore, QtWidgets

# # Path to your wordlist file (adjust if necessary)
# WORDLIST_PATH = r"google-10000-english-no-swears.txt"


# # Try to import the user's function. If it's not available,
# # we provide a helpful fallback that raises an exception when called.
# try:
#     from minimum_edit_distance  import get_the_nearest_strings  # try project-specific module
# except Exception:
#     # If that import fails, try to find it in the current namespace (maybe the user defined it)
#     try:
#         get_the_nearest_string  # type: ignore
#     except Exception:
#         # fallback stub: informs the user to provide the real function
#         def get_the_nearest_strings(query: str, wordlist_path: str) -> List[str]:
#             raise RuntimeError(
#                 "get_the_nearest_string not found. Provide this function in scope "
#                 "or place it in suggestions.py. It should accept (str, path) "
#                 "and return a list of suggestions."
#             )


# class SuggestWorker(QtCore.QObject):
#     """
#     Worker object that runs get_the_nearest_string in another thread.
#     """
#     finished = QtCore.pyqtSignal(list)         # emits the suggestions list
#     error = QtCore.pyqtSignal(str)             # emits error messages

#     def __init__(self, word: str, wordlist_path: str):
#         super().__init__()
#         self.word = word
#         self.wordlist_path = wordlist_path

#     @QtCore.pyqtSlot()
#     def run(self):
#         """Execute the suggestion function."""
#         try:
#             # Call user-provided function (assumed to return list-like)
#             result = minimum_edit_distance.get_the_nearest_strings(self.word, self.wordlist_path)
#             # Ensure it's a list or iterable of strings
#             if result is None:
#                 result = []
#             if not isinstance(result, (list, tuple)):
#                 # try converting to list
#                 try:
#                     result = list(result)
#                 except Exception:
#                     raise TypeError("get_the_nearest_string must return a list/iterable of strings.")
#             # Keep only up to 5 suggestions to match UI expectation
#             suggestions = result[:5]
#             self.finished.emit(suggestions)
#         except Exception as e:
#             tb = traceback.format_exc()
#             self.error.emit(f"{e}\n\n{tb}")


# class MainWindow(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("word suggestions")
#         self.resize(520, 300)
#         self._setup_ui()
#         self.thread = None
#         self.worker = None

#     def _setup_ui(self):
#         # Central widget + layout
#         central = QtWidgets.QWidget()
#         self.setCentralWidget(central)
#         vbox = QtWidgets.QVBoxLayout(central)
#         vbox.setContentsMargins(12, 12, 12, 12)
#         vbox.setSpacing(10)

#         # Input area
#         input_layout = QtWidgets.QHBoxLayout()
#         lbl = QtWidgets.QLabel("Type a word:")
#         lbl.setFixedWidth(90)
#         input_layout.addWidget(lbl)

#         self.input_edit = QtWidgets.QLineEdit()
#         self.input_edit.setPlaceholderText("Enter word to correct (press Enter or click Suggest)")
#         self.input_edit.returnPressed.connect(self.on_suggest_clicked)
#         input_layout.addWidget(self.input_edit)

#         self.suggest_btn = QtWidgets.QPushButton("Suggest")
#         self.suggest_btn.clicked.connect(self.on_suggest_clicked)
#         input_layout.addWidget(self.suggest_btn)

#         vbox.addLayout(input_layout)

#         # Suggestions area
#         suggestions_label = QtWidgets.QLabel("Top suggestions (double-click to use):")
#         vbox.addWidget(suggestions_label)

#         self.suggestions_list = QtWidgets.QListWidget()
#         self.suggestions_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
#         self.suggestions_list.itemDoubleClicked.connect(self.on_suggestion_double_clicked)
#         vbox.addWidget(self.suggestions_list, stretch=1)

#         # Status bar
#         self.status = QtWidgets.QStatusBar()
#         self.setStatusBar(self.status)
#         self.status.showMessage("Ready")

#         # Simple stylesheet for a cleaner look
#         self.setStyleSheet("""
#             QLabel { font-size: 12px; }
#             QLineEdit { font-size: 13px; padding: 6px; }
#             QPushButton { padding: 6px; font-size: 13px; }
#             QListWidget { font-size: 13px; padding: 4px; }
#         """)

#     def on_suggest_clicked(self):
#         word = self.input_edit.text().strip()
#         if not word:
#             self.status.showMessage("Please type a word first.")
#             return

#         # Disable button and start worker thread
#         self.suggest_btn.setEnabled(False)
#         self.input_edit.setEnabled(False)
#         self.suggestions_list.clear()
#         self.status.showMessage("Searching...")

#         # Create a QThread and worker
#         self.thread = QtCore.QThread()
#         self.worker = SuggestWorker(word, WORDLIST_PATH)
#         self.worker.moveToThread(self.thread)
#         self.thread.started.connect(self.worker.run)
#         self.worker.finished.connect(self.on_worker_finished)
#         self.worker.error.connect(self.on_worker_error)
#         # Cleanup when done
#         self.worker.finished.connect(self.thread.quit)
#         self.worker.error.connect(self.thread.quit)
#         self.thread.finished.connect(self._cleanup_thread)
#         self.thread.start()

#     def on_worker_finished(self, suggestions: list):
#         # Populate the list widget
#         self.suggestions_list.clear()
#         if not suggestions:
#             self.suggestions_list.addItem("(no suggestions)")
#             self.status.showMessage("No suggestions found.")
#         else:
#             for s in suggestions:
#                 item = QtWidgets.QListWidgetItem(str(s))
#                 self.suggestions_list.addItem(item)
#             self.status.showMessage(f"Found {len(suggestions)} suggestion(s).")

#         # Re-enable controls
#         self.suggest_btn.setEnabled(True)
#         self.input_edit.setEnabled(True)
#         self.input_edit.setFocus()

#     def on_worker_error(self, message: str):
#         # Show error in a dialog and status bar
#         self.suggestions_list.clear()
#         self.suggestions_list.addItem("(error while getting suggestions)")
#         QtWidgets.QMessageBox.critical(self, "Suggestion Error", str(message))
#         self.status.showMessage("Error occurred - see dialog for details.")
#         self.suggest_btn.setEnabled(True)
#         self.input_edit.setEnabled(True)
#         self.input_edit.setFocus()

#     def _cleanup_thread(self):
#         # Properly delete worker and thread references
#         try:
#             if self.worker:
#                 self.worker.deleteLater()
#             if self.thread:
#                 self.thread.deleteLater()
#         finally:
#             self.worker = None
#             self.thread = None

#     def on_suggestion_double_clicked(self, item: QtWidgets.QListWidgetItem):
#         text = item.text()
#         if text and text != "(no suggestions)" and text != "(error while getting suggestions)":
#             self.input_edit.setText(text)
#             # Optionally, auto re-run suggestion for the newly filled word:
#             # self.on_suggest_clicked()


# def main():
#     app = QtWidgets.QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())


# if __name__ == "__main__":
#     main()

# project_ui_live.py
import sys
import traceback
from typing import List, Optional

from PyQt5 import QtCore, QtWidgets

# Path to your wordlist file (adjust if necessary)
WORDLIST_PATH = r"google-10000-english-no-swears.txt"

# Try to import the user's function from minimum_edit_distance.
# It should be: get_the_nearest_strings(query: str, wordlist_path: str) -> List[str]
try:
    import minimum_edit_distance
    _get_suggestions_fn = getattr(minimum_edit_distance, "get_the_nearest_strings")
except Exception:
    _get_suggestions_fn = None


class SuggestWorker(QtCore.QObject):
    """
    Worker object that runs minimum_edit_distance.get_the_nearest_strings in another thread.
    Emits the word it requested along with the suggestions so the main thread can verify.
    """
    finished = QtCore.pyqtSignal(str, list)   # (queried_word, suggestions_list)
    error = QtCore.pyqtSignal(str)            # error message

    def __init__(self, word: str, wordlist_path: str):
        super().__init__()
        self.word = word
        self.wordlist_path = wordlist_path

    @QtCore.pyqtSlot()
    def run(self):
        try:
            if _get_suggestions_fn is None:
                raise RuntimeError(
                    "get_the_nearest_strings not found. Provide this function in minimum_edit_distance.py "
                    "and ensure it's importable."
                )
            result = _get_suggestions_fn(self.word, self.wordlist_path)
            if result is None:
                result = []
            if not isinstance(result, (list, tuple)):
                try:
                    result = list(result)
                except Exception:
                    raise TypeError("get_the_nearest_strings must return a list/iterable of strings.")
            suggestions = result[:5]
            self.finished.emit(self.word, suggestions)
        except Exception as e:
            tb = traceback.format_exc()
            self.error.emit(f"{e}\n\n{tb}")


class MainWindow(QtWidgets.QMainWindow):
    DEBOUNCE_MS = 300

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autocorrect")
        self.resize(560, 320)
        self._setup_ui()

        # threading / scheduling state
        self.thread: Optional[QtCore.QThread] = None
        self.worker: Optional[SuggestWorker] = None

        self.debounce_timer = QtCore.QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._on_debounce_timeout)

        self.pending_word: Optional[str] = None         # word scheduled after debounce
        self.next_pending_word: Optional[str] = None    # queued word while worker running
        self.last_requested_word: Optional[str] = None  # last word we asked suggestions for

        # connect live typing
        self.input_edit.textChanged.connect(self.on_text_changed)

    def _setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        vbox = QtWidgets.QVBoxLayout(central)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(10)

        input_layout = QtWidgets.QHBoxLayout()
        lbl = QtWidgets.QLabel("Type text:")
        lbl.setFixedWidth(90)
        input_layout.addWidget(lbl)

        self.input_edit = QtWidgets.QLineEdit()
        self.input_edit.setPlaceholderText("Type text — suggestions update as you type words")
        input_layout.addWidget(self.input_edit)

        self.suggest_btn = QtWidgets.QPushButton("Suggest")
        self.suggest_btn.clicked.connect(self.on_manual_suggest_clicked)
        input_layout.addWidget(self.suggest_btn)

        vbox.addLayout(input_layout)

        suggestions_label = QtWidgets.QLabel("Top suggestions (double-click to replace current word):")
        vbox.addWidget(suggestions_label)

        self.suggestions_list = QtWidgets.QListWidget()
        self.suggestions_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.suggestions_list.itemDoubleClicked.connect(self.on_suggestion_double_clicked)
        vbox.addWidget(self.suggestions_list, stretch=1)

        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

        self.setStyleSheet("""
            QLabel { font-size: 12px; }
            QLineEdit { font-size: 13px; padding: 6px; }
            QPushButton { padding: 6px; font-size: 13px; }
            QListWidget { font-size: 13px; padding: 4px; }
        """)

    # ---------------------------
    # Text handling / tokenization
    # ---------------------------
    def get_current_word(self) -> str:
        """Return the last token after the final space. If last char is a space, returns empty string."""
        text = self.input_edit.text()
        if text == "":
            return ""
        # If last char is space, user finished the word — we consider current word empty
        if text and text[-1].isspace():
            return ""
        # split on spaces and take last piece
        parts = text.rsplit(" ", 1)
        if len(parts) == 1:
            return parts[0]
        return parts[1]

    def replace_current_word(self, new_word: str):
        """
        Replace only the current (last) token in the input with new_word.
        If there was trailing whitespace after the word, we keep the trailing space.
        """
        text = self.input_edit.text()
        trailing_space = ""
        if text.endswith(" "):
            # if text ended with space, current word was empty; just append new_word
            new_text = text + new_word
        else:
            # replace the last token
            parts = text.rsplit(" ", 1)
            if len(parts) == 1:
                new_text = new_word
            else:
                new_text = parts[0] + " " + new_word
        # set text and put cursor at the end
        self.input_edit.setText(new_text)
        self.input_edit.setCursorPosition(len(new_text))

    # ---------------------------
    # Live suggestion scheduling
    # ---------------------------
    def on_text_changed(self, _unused_text: str):
        """
        Called on every text change. We examine the current word and:
         - if it's empty (user typed a space), clear suggestions
         - otherwise debounce and schedule a suggestion for the current word
        """
        current_word = self.get_current_word()
        # If user typed a space (current_word == ""), clear suggestions and do nothing
        if current_word == "":
            self.suggestions_list.clear()
            self.status.showMessage("Ready (space detected — tracking next word).")
            # cancel any pending debounce
            self.debounce_timer.stop()
            self.pending_word = None
            # also reset queued next word since there's no active current word
            self.next_pending_word = None
            return

        # If same as last requested word, do nothing
        if current_word == self.last_requested_word or current_word == self.pending_word:
            # nothing changed meaningfully for suggestions
            return

        # schedule debounce
        self.pending_word = current_word
        self.debounce_timer.start(self.DEBOUNCE_MS)
        self.status.showMessage(f"Waiting to query suggestions for '{current_word}'...")

    def _on_debounce_timeout(self):
        """Debounce fired; start worker or queue if a worker is running."""
        word = self.pending_word
        if not word:
            return
        # If a worker is currently running, queue this word to start after current finishes
        if self.thread is not None and self.thread.isRunning():
            self.next_pending_word = word
            self.status.showMessage(f"Queued suggestions for '{word}' (waiting current request).")
            return
        # Otherwise start a worker immediately
        self._start_worker_for(word)

    # ---------------------------
    # Worker lifecycle
    # ---------------------------
    def _start_worker_for(self, word: str):
        """Start a SuggestWorker in a QThread for the given word."""
        self.last_requested_word = word
        self.status.showMessage(f"Searching suggestions for '{word}'...")
        self.thread = QtCore.QThread()
        self.worker = SuggestWorker(word, WORDLIST_PATH)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.error.connect(self.on_worker_error)

        # cleanup / chaining
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self._on_thread_finished)

        # start
        self.thread.start()

    def on_worker_finished(self, queried_word: str, suggestions: list):
        """
        Called when a worker finishes. Only update UI if the queried_word matches the
        current word (so old results don't overwrite newer ones).
        """
        current_word = self.get_current_word()
        # Only update suggestions if the word still matches user's current word
        if queried_word == current_word:
            self.suggestions_list.clear()
            if not suggestions:
                self.suggestions_list.addItem("(no suggestions)")
                self.status.showMessage(f"No suggestions for '{queried_word}'.")
            else:
                for s in suggestions:
                    self.suggestions_list.addItem(str(s))
                self.status.showMessage(f"Found {len(suggestions)} suggestion(s) for '{queried_word}'.")
        else:
            # ignore outdated results
            self.status.showMessage(f"Ignored results for '{queried_word}' (user typed '{current_word}' afterwards).")

    def on_worker_error(self, message: str):
        self.suggestions_list.clear()
        self.suggestions_list.addItem("(error while getting suggestions)")
        QtWidgets.QMessageBox.critical(self, "Suggestion Error", str(message))
        self.status.showMessage("Error occurred - see dialog for details.")

    def _on_thread_finished(self):
        """Cleanup after thread terminates, and start next pending if any."""
        # delete worker & thread safely
        try:
            if self.worker:
                self.worker.deleteLater()
            if self.thread:
                self.thread.deleteLater()
        finally:
            self.worker = None
            self.thread = None

        # If there's a queued word to request, and it's different from last requested, start it
        if self.next_pending_word and self.next_pending_word != self.last_requested_word:
            next_word = self.next_pending_word
            self.next_pending_word = None
            # start next worker
            # schedule a tiny delay to allow event loop to clean up (optional)
            QtCore.QTimer.singleShot(10, lambda: self._start_worker_for(next_word))
        else:
            # nothing queued
            self.status.showMessage("Ready")

    # ---------------------------
    # Manual suggest button
    # ---------------------------
    def on_manual_suggest_clicked(self):
        """Manual suggest button triggers immediate suggestion for current word (cancels debounce)."""
        self.debounce_timer.stop()
        self.pending_word = None
        current_word = self.get_current_word()
        if not current_word:
            self.status.showMessage("No current word to suggest for.")
            return
        # If a worker is running, queue this request to run next; otherwise start immediately.
        if self.thread is not None and self.thread.isRunning():
            self.next_pending_word = current_word
            self.status.showMessage(f"Queued manual suggestion for '{current_word}'.")
        else:
            self._start_worker_for(current_word)

    # ---------------------------
    # Suggestion interaction
    # ---------------------------
    def on_suggestion_double_clicked(self, item: QtWidgets.QListWidgetItem):
        text = item.text()
        if not text:
            return
        if text in ("(no suggestions)", "(error while getting suggestions)"):
            return
        # Replace current word with clicked suggestion
        self.replace_current_word(text)
        # After replacing, clear suggestions (or you might want to query suggestions for the replaced word)
        self.suggestions_list.clear()
        self.status.showMessage(f"Replaced current word with '{text}'.")

        # Optionally, run suggestions for new (replaced) word if it's still the current token (no trailing space)
        # self.on_manual_suggest_clicked()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
