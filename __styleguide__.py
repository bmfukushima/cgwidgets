class StyleGuide(object):
    """
    Definition of this class

    This is the second paragraph of the definition of this class

    Args:
        argument (type): This is the first line of the argument.

    Kwargs:
        argument (type): This is the first line of the argument.

    Attributes/Properties:
        + Public +
        Internal Notes:
            * use getters / setters
                ie.
                    getPropertyName()
                    setPropertyName(value)
            * attributes and properties use the _ syntax
                ie
                    this_is_an_attribute

        attribute_name (type): This is the first line of the argument.

        Notes:
            * This is a note, hurray!
            * This section is for any additional notes for the developer

        - Private -
        Internal Notes:
            * private attributes use the @property for getters/setters

        private_attr_name (type): This is the first line of the argument.
            second line of the private attr maybe with some more information
            or something like that
        another_private_attr (type): This is the first line of another private attr
            and it goes to the second line, which is indented.

            You can also add paragraphs.. but this looks like garbage.. because
            there should not be a larger seperation between paragraphs than
            there is between attrs.. or seconds...

        Notes:
            * This is a note, hurray!
            * This section is for any additional notes for the developer

    """

    def __init__(self):
        pass

    """ API """
    def getProperty(self):
        return self._property

    def setProperty(self, _property):
        self._property = _property

    """ PROPERTIES """
    @property
    def user_property(self):
        return self._property

    @user_property.setter
    def user_property(self, user_property):
        self._property = user_property

    """ UTILS """
    def utils(self, arg, kwarg=None):
        """
        Definition of this class

        This is the second paragraph of the definition of this class

        Args:
            argument (type): This is the first line of the argument.

        Kwargs:
            argument (type): This is the first line of the argument.

        Returns:
            (type): This is the first line of the argument.
        """
        pass

    """ EVENTS """


