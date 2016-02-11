#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import QDoubleSpinBox, QRegExpValidator, QAbstractSpinBox, QApplication
from PyQt4.QtCore import QRegExp, Qt, QTranslator, QLocale, QLibraryInfo


class LM_DoubleSpinBox_with_calc(QDoubleSpinBox):
    '''
    This class is a special spinbox which allows the user to enter a math-expression. As soon as the edit is finished
    the expression will be evaluated and result will be entered in spinBox.
    To evaluate if the entered formula is valid, check "canBeCommitted" (bool). If true, you can read value.
    IMPORTANT: You can not use any "suffix" or "prefix" (which is ignoring the Regex...)
    '''

    def __init__(self, parent=None):
        super(LM_DoubleSpinBox_with_calc, self).__init__(parent)
        #setup a special validator (allowed are leading '=', 0-9 , . ( ) * / + - ... no caracters ... excel-like
        self.validator = QRegExpValidator(QRegExp("(^={1}\d*([-+*/(),.]*\d*)*)|([0-9,.])*"))
        self.expression = ""   # this is the variable which holds the expression
        self.setSpecialValueText("")   # this is only an action to avoid error messages if the field is empty
        self.setCorrectionMode(QAbstractSpinBox.CorrectToPreviousValue)
        self.canBeCommitted = True  #this variable holds the status, if the user has entered a valid formula or not

    def valueFromText(self, string):
        '''
        If the user has entered "anything" and hit enter or focus is lost, this function will be called, the
        call is overloaded with the entered string.
        :param string:Value entered in Widget as string
        :return: float (from string)
        '''
        string = string.replace(",", ".")   #tanslate from "german" floating point value
        if string.startsWith("="):
            self.expression = string
            self.setFocusPolicy(Qt.StrongFocus)
            return float(self.value()) #dont forget about the value if user is entering a formula
        elif string.isEmpty():
            return float(self.value())  #dont forget about the value if user has cleared the lineEdit
        return float(string)

    def textFromValue(self, p_float):
        '''
        This function is called, when a value (float) should be "displayed", which have to be a string.
        :param p_float: float()
        :return: String from float
        '''
        if self.expression != "":
            expression = self.expression.replace("=", "").replace(",",".")  #forget about the "="
            try:
                result = float(eval(str(expression)))          #calculate the expression
                self.expression = ""
                self.setValue(result)                          #set the "value"
            except SyntaxError:  #this should not happen, because the formula is evaluated fist with "inValidCalculation"
                #print("There was a syntaxError, returning", self.expression)
                result = "="+self.expression
            return "{0}".format(result).replace(".", ",")  #return the display presentation of the value (string)
        return "{0}".format(p_float).replace(".", ",")     #if the exression is empty, only return the string

    def validate(self, string, p_int):
        '''
        Function overrides builtin.
        Is more or less only a "switch" for bool "canBeCommited" which is true, if user has currently entered a valid
        math formula
        :param string: "content of current Spinbox"
        :param p_int: "count which should be validated"
        :return:
        '''
        if string.startsWith("="):
            if self.isValidCalculation(string):
                self.canBeCommitted = True
                return self.validator.validate(string, p_int)
            else:
                self.canBeCommitted = False
                return self.validator.validate(string, p_int)
        else:
            self.canBeCommitted =True
            return self.validator.validate(string, p_int)

    def isValidCalculation(self, string):
        '''
        Ducktyped: if the string is a valid formula which can be evaluated, this function returns True, otherwise
        False
        :param string: QString / String containing a math formula
        :return: True if valid, otherwise false.
        '''
        try:
            float(eval(str(string).replace("=", "").replace(",",".") ))          #calculate the expression
            return True
        except:
            return False

if __name__ == "__main__":
    app = QApplication([sys.argv])
    qt_translator = QTranslator()
    qt_translator.load("qt_" + QLocale.system().name(),
                       QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qt_translator)
    widget = LM_DoubleSpinBox_with_calc()
    widget.show()
    sys.exit(app.exec_())