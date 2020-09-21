class iDynamicWidget(object):
    def setDynamicWidgetBaseClass(self, widget):
        """
        Sets the constructor for the dynamic widget.  Everytime
        a new dynamic widget is created. It will use this base class
        """
        self._dynamic_widget_base_class = widget

    def getDynamicWidgetBaseClass(self):
        if hasattr(self, '_dynamic_widget_base_class'):
            return self._dynamic_widget_base_class
        return None

    def setDynamicUpdateFunction(self, function):
        self._dynamicWidgetFunction = function

    def getDynamicUpdateFunction(self):
        if self._dynamicWidgetFunction:
            return self._dynamicWidgetFunction
        return None
