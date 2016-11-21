#------------------------------------------------------------------------------

'''
    Automation exception class

    Error Code              Failure point
    ---------------------------------------------------------------------------

        1                   Failed to land on login page
        2                   Failed to login
        3                   Failed to complete query
        4                   Failed to reach document page;
                                reached "search results" page instead
    ---------------------------------------------------------------------------
'''

#------------------------------------------------------------------------------




class InvalidLanding(Exception):
    def __init__(self, code, message=""):
        if not message:
            super().__init__("Invalid landing at stage {}.".format(code))
        else:
            super().__init__(
                "Invalid landing at stage {}, with exit message {}.".format(code, message)
            )
