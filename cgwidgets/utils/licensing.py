""" Super simple licensing app, I'd prefer if you didn't steal the software, but I'm not going to make it that hard to steal."""

import datetime
import os
import calendar

DECRYPTION = {
"QLKJSDFN":"0",
"LKDFSJQP":"1",
"ALKJDFWJ":"2",
"SFAKJQ>!":"3",
"SLKJDFM@":"4",
"!&SD><MD":"5",
"!)(*&SDK":"6",
"KLSJ!#DJ":"7",
"DKJL)!KD":"8",
"J!)X^M!(":"9"}

ENCRPYTION = [x for x in DECRYPTION.keys()]
NUM_CIPHER_DIGITS = 8


def generateLicense(day, month, year, filepath=None):
    """ Generates a simple Ceasar cipher license

    Args:
        day (str): XX format
        month (str): XX format
        year (str): XXXX format
        filepath (str): path on disk to save license to, if none is provided, this will
            default to the local path.


        """
    if not filepath:
        filepath = "license.txt"

    day = ENCRPYTION[int(day[0])] + ENCRPYTION[int(day[1])]
    month = ENCRPYTION[int(month[0])] + ENCRPYTION[int(month[1])]
    year = ENCRPYTION[int(year[0])] + ENCRPYTION[int(year[1])] + ENCRPYTION[int(year[2])] + ENCRPYTION[int(year[3])]

    with open(filepath, 'a') as f:
        f.truncate(0)
        f.write(day + month + year)
    return day + month + year


def checkLicenseFile(filepath):
    today = datetime.date.today()

    with open(filepath, "r") as f:
        license_date = f.readlines()[0]

    try:
        str_license_day = license_date[:2*NUM_CIPHER_DIGITS]
        license_day = int(DECRYPTION[str_license_day[0:NUM_CIPHER_DIGITS]] + DECRYPTION[str_license_day[NUM_CIPHER_DIGITS:NUM_CIPHER_DIGITS*2]])
        str_license_month = license_date[2*NUM_CIPHER_DIGITS:4*NUM_CIPHER_DIGITS]
        license_month = int(DECRYPTION[str_license_month[0:NUM_CIPHER_DIGITS]] + DECRYPTION[str_license_month[NUM_CIPHER_DIGITS:NUM_CIPHER_DIGITS*2]])
        str_license_year = license_date[4*NUM_CIPHER_DIGITS:8*NUM_CIPHER_DIGITS]
        license_year = int(DECRYPTION[str_license_year[:NUM_CIPHER_DIGITS]] + DECRYPTION[str_license_year[NUM_CIPHER_DIGITS:NUM_CIPHER_DIGITS*2]] + DECRYPTION[str_license_year[NUM_CIPHER_DIGITS*2:NUM_CIPHER_DIGITS*3]] + DECRYPTION[str_license_year[NUM_CIPHER_DIGITS*3:NUM_CIPHER_DIGITS*4]])

        # check year
        if license_year < today.year: return False
        elif today.year < license_year: return True

        # if current year, check month
        if license_month < today.month: return False
        if today.month < license_month: return True

        # if current month, check day
        if license_day + 1 < today.day: return False

        return True

    # cannot find hash
    except KeyError:
        return False


def licenseDate(filepath):
    """ Returns the date of the license file"""
    with open(filepath, "r") as f:
        license_date = f.readlines()[0]

    try:
        str_license_day = license_date[:2 * NUM_CIPHER_DIGITS]
        license_day = int(DECRYPTION[str_license_day[0:NUM_CIPHER_DIGITS]] + DECRYPTION[str_license_day[NUM_CIPHER_DIGITS:NUM_CIPHER_DIGITS * 2]])
        str_license_month = license_date[2 * NUM_CIPHER_DIGITS:4 * NUM_CIPHER_DIGITS]
        license_month = int(DECRYPTION[str_license_month[0:NUM_CIPHER_DIGITS]] + DECRYPTION[str_license_month[NUM_CIPHER_DIGITS:NUM_CIPHER_DIGITS * 2]])
        str_license_year = license_date[4 * NUM_CIPHER_DIGITS:8 * NUM_CIPHER_DIGITS]
        license_year = int(DECRYPTION[str_license_year[:NUM_CIPHER_DIGITS]] + DECRYPTION[str_license_year[NUM_CIPHER_DIGITS:NUM_CIPHER_DIGITS * 2]] + DECRYPTION[str_license_year[NUM_CIPHER_DIGITS * 2:NUM_CIPHER_DIGITS * 3]] + DECRYPTION[str_license_year[NUM_CIPHER_DIGITS * 3:NUM_CIPHER_DIGITS * 4]])

        license_month = calendar.month_name[license_month]
        return f"{license_day} {license_month} {license_year}"

    except (KeyError, NameError):
        # Invalid license
        return "Invalid license"


def checkLicenseFiles(filepaths):
    for filepath in filepaths:
        if os.path.isfile(filepath):
            if checkLicenseFile(filepath):
                return (True, filepath)
        print(f"No license found at {filepath}")

    return (False, None)

