# import the necessary packages
# import PyPDF2
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
from PIL import Image
import fnmatch
import pytesseract
import re
import os
import datetime


def getReceipt(image_filename):
    """
    returns a text after OCR was conducted on image filename.

        \param image_filename: filename of the image, e.g., receipt.jpg.

        \return text string.
    """
    image_filename_pdf = convert_from_path(image_filename)

    #    return pytesseract.image_to_string(Image.open(image_filename))
    return pytesseract.image_to_string(image_filename_pdf[0])


def getBizName(receipt_in_list):
    """
    get biz name using receipt list passed as parameter.

        \param receipt_in_list: list that contains receipt content.  Each line is contained in an item.

        \return text string with name.
    """

    business_name = receipt_in_list[0]

    if not business_name:
        biz_search = " "
    else:
        biz_search = re.search("^[ ]*$", business_name)

    if biz_search is not None:
        business_name = "unknown biz"

    business_name = business_name.replace("-", " ").replace("'", "").lower()

    return business_name


def __getValidDate(string_date):
    string_length = len(string_date)

    month = int(string_date[0:2])
    day = int(string_date[3:5])
    year = 0

    if string_length == 8:

        year = 2000 + int(string_date[6:9])

    elif string_length == 10:

        year = int(string_date[6:11])

    else:

        return None

    if 1 < month > 12:
        return None

    if 1 < day > 31:
        return None

    if 2019 < year > 2020:
        return None

    return_valid_date = datetime.date(year, month, day)

    return return_valid_date


def getDate(receipt_in_list):
    """
    get biz receipt date using receipt list passed as parameter.

        \param receipt_in_list: list that contains receipt content.  Each line is contained in an item.

        \return text string with date in format YYYY-MM-DD, e.g., 2019-02-08.
    """

    date_set = set()

    for item in receipt_in_list:
        result = re.search("[0-9]{2}[/-][0-9]{2}[/-](20)?[0-9]{2}", item)
        if result is not None:
            actual_date = __getValidDate(result.group())
            if actual_date is not None:
                date_set.add(actual_date)

    if len(date_set) != 0:
        return date_set.pop().strftime("%Y-%m-%d")
    else:
        return "1970-01-01"


def getTotal(receipt_in_list):
    """
      get biz receipt total using receipt list passed as parameter.

          \param receipt_in_list: list that contains receipt content.  Each line is contained in an item.

          \return float number with dollar amount XX.XX, e.g., 36.54
      """

    total_set = set()

    for item in receipt_in_list:
        result = re.search("[ ]*[0-9]*\.[0-9]{2}", item)

        if result is not None:
            total = float(result.group())
            total_set.add(total)
        else:
            total_set.add(0.0)

    return max(total_set)


def getFilename(receipt_in_list):
    """
      get biz receipt total using receipt list passed as parameter.

          \param receipt_in_list: list that contains receipt content.  Each line is contained in an item.

          \return a filename in string format as follows: YYYY-MM-DD-Biz Name-$XXX.XX
      """
    biz_name = getBizName(receipt_in_list)
    biz_date = getDate(receipt_in_list)
    biz_total = getTotal(receipt_in_list)

    return_filename = "{}-{}-${}".format(biz_date, biz_name, biz_total)

    return return_filename


def match_results_summary (result_list):

    data_count = len(result_list)
    date_equal = 0
    name_equal = 0
    price_equal = 0

    for data in result_list:
        date_equal += data["date equal"]
        name_equal += data["name equal"]
        price_equal += data["price equal"]

    return "date: {1}/{0}: {2} %\n" \
           "name: {3}/{0}: {4} %\n" \
           "price: {5}/{0}: {6} %".format(data_count,
                                          date_equal, date_equal*100/data_count,
                                          name_equal, name_equal*100/data_count,
                                          price_equal, price_equal*100/data_count)


def compare_filenames(standard_file, automatic_file):
    results = {"original file": standard_file,
               "computer file": automatic_file,
               "date equal": 0,
               "name equal": 0,
               "price equal": 0}

    std_list = standard_file.split("-")
    auto_list = automatic_file.split("-")

    std_date = std_list[0] + "-" + std_list[1] + "-" + std_list[2]
    auto_date = auto_list[0] + "-" + auto_list[1] + "-" + auto_list[2]

    if std_date == auto_date:
        results["date equal"] = 1

    if std_list[3] == auto_list[3]:
        results["name equal"] = 1

    std_price = std_list[4].split(".pdf")
    auto_price = std_list[4].split(".pdf")

    if std_price is None:
        std_price = "0.0"

    if auto_price is None:
        auto_price = "0.0"

    std_price = std_price[0].replace("$", "")
    auto_price = auto_price[0].replace("$", "")

    if std_price == auto_price:
        results["price equal"] = 1

    return results


if __name__ == "__main__":

    __path = "."
    #    __filename = fnmatch.filter(os.listdir(__path), '*.jpg')
    __filename = fnmatch.filter(os.listdir(__path), '*.pdf')

    result_list = []

    for __file in __filename:
        __text_file = getReceipt(__file)

        __list_file = __text_file.split("\n")

        # print(__list_file)

        __the_filename = getFilename(__list_file) + ".pdf"

        print(__file)
        print(__the_filename)

        compare_results = compare_filenames(__file, __the_filename)

        result_list.append(compare_results)
        print(compare_results)

    print("\n"+match_results_summary(result_list))