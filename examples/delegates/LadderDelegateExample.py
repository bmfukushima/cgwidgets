import sys
from qtpy.QtWidgets import QApplication, QVBoxLayout, QWidget
from qtpy.QtGui import QCursor

from cgwidgets.widgets import FloatInputWidget, IntInputWidget
from cgwidgets.utils import installLadderDelegate, setAsBorderless
from cgwidgets.settings import iColor


app = QApplication(sys.argv)

main_window = QWidget()

# setup style for documenting
setAsBorderless(main_window)
main_window.setStyleSheet("""background-color:rgba{rgba_background_00}""".format(**iColor.style_sheet_args))
main_layout = QVBoxLayout()
main_layout.setContentsMargins(50, 50, 50, 50)

main_window.setLayout(main_layout)

# install ladder delegate with utils function
float_input_widget = FloatInputWidget(do_math=True)
float_input_widget.setDoMath(True)
ladder = installLadderDelegate(float_input_widget, allow_zero_value=True, allow_negative_values=False)
float_input_widget.setText('12.3')

# install ladder delegate with widget function
int_input_widget = IntInputWidget()
int_input_widget.setUseLadder(True, value_list=[1, 2, 4, 8, 16, 32])


main_layout.addWidget(float_input_widget)
main_layout.addWidget(int_input_widget)
main_window.show()
main_window.move(QCursor.pos())

sys.exit(app.exec_())