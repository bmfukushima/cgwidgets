class StyleGuide(object):
    """
A one line summary of the module or program, terminated by a period.

One blank line follows the 80 char summary.  Very twitter like, now I see
where we got Twitter from...

But Twitter doesn't allow you to have an entire summary... or yet a
second paragraph! Which is seperated by space...

I'm using tabs or 4 spaces here... I'm using tabs because I like my
space bar because its my jump key in games, and I don't want to spam
that all day and break my keyboard... I mean this thing is rated at 50m
keystrokes if ya know what I mean ;)

Args:
    Arguments should be denoted if they are an *arg, or a **kwarg
    by using * or ** followed by spaces.  This should do a total line
    fill of four characters or the number of spaces that a tab will use.
    Please note the double tab on the proceeding lines of text after
    the one line summary.
        *   argument (type): This is the first line of the argument.
                However, sometimes a second line is required, and
                these arguments are like the energize bunny, and
                they just keep on going, and going, and going, and
                going, and going, and going, and also please use
                oxford commas.
        *   argument2 (type): These argument descriptions however,
                should be limited to a maximum of one paragraph.  If you
                are typing more than a paragraph to describe an attribute,
                then you did something wrong.  As at a bare minimum,
                you broke the doc string conventions style good you noob.
        *   argument3 (type): This is the first line of the argument.
        **  kwarg (type): Optional kwarguement, however, I need to
                keep writing text until I get to atleast a second line.  This
                should do, so I'll stop typing stuff now.
        **  another_kwarg (type): A second kwarg...

Attributes:
    Attributes are broken down into public vs private.
    The primary definition to determine what is public and what
    is private is if it will be exposed as an API call.  If it is an API
    then it is public, if it is not an API call then it is private.
    -   use getters / setters
            ie.
                getPropertyName()
                setPropertyName(value)
    -   attributes and properties use the _ syntax
            ie: this_is_an_attribute
        *   attribute (type): one line description
                If more information on the attribute is needed, a second
                line can be added.  However, this should not proceed
                more than one paragraph of information.  Mainly because
                I don't like how spaces look in the visual formatting, as they
                provide an awkward looking seperation of information, due to
                the uniformity of display text.
        *   attribute (type): Oddly enough, you add a space between
                paragraphs in the description.  But not between attributes.

Notes:
    -   This section is for any additional notes that the I think are necessary
            for someone else to know.  Please note the continuued usaged of
            the 4 padded delimietors between items in this case, '-' followed
            by three ' '.

Syntax
    attribute:
        this_is_an_attribute
        public:
            define with getters/setters
        private:
            define with @property decorator
    method:
        thisIsAMethod()
    class:
        ThisIsAClass()
--------------------------------------------------------------------------------
    """

    def __init__(self):
        pass

    """ API """
    def getPublicAttr(self):
        return self._public_attr

    def setPublicAttr(self, _public_attr):
        self._property = _public_attr

    """ PROPERTIES """
    @property
    def private_attribute(self):
        """
        private_attribute (type): This is the first line of the argument.
            This is written in the @property method of the private_attribute
            method.
        """
        return self._property

    @private_attribute.setter
    def private_attribute(self, private_attribute):
        self._property = private_attribute

    """ UTILS """
    def utils(self, arg, kwarg=None):
        """
        One line description of this function.

        This is the second paragraph of the definition of this class.
        These doc strings should be written in the class themselves
        in order to not muddy up the class doc string.

        Args:
            *   argument (type): This is the first line of the argument.
                    This is the second line, please note the 8 space or
                    double tab indention.
            *   argument (type): This is the first line of the argument.
            **  kwarg (type): Optional kwarguement
            **  another_kwarg (type): A second kwarg...

        Returns:
            (type): This is the first line of the argument.
        """
        pass

    def exampleDocString(self, arg, kwarg=None):
        """
        One line description of this function.

        Args:
            *   argument (type): This is the first line of the argument.
                    This is the second line, please note the 8 space or
                    double tab indention.
            **  kwarg (type): Optional kwarguement

        Returns:
            (type): This is the first line of the argument.
        """
        pass
    """ EVENTS """


if __name__ == '__main__':
    from qtpy.QtWidgets import QWidget

    print(help(StyleGuide))

