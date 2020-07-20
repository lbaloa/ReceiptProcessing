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


def getBizPair(search_item, bizname):
    """
    getBizPair returns a dictionary that associates search_item to bizname.

        \param search_item, e.g., ' 309 Lake Forest'

        \param bizname, e.g., daiso

        \return dictionary
    """
    return {'search_item': search_item.lower(), 'bizname': bizname.lower()}


def getBizName(receipt_in_list):
    """
    get biz name using receipt list passed as parameter.

        \param receipt_in_list: list that contains receipt content.  Each line is contained in an item.

        \return text string with name.
    """

    search_list_dic = [getBizPair('9 Lake Forest', '99c'),
                       getBizPair('789 South Tustin Street', '99c'),
                       getBizPair('765 South', '99c'),
                       getBizPair('4045 Lake Forest', 'daiso'),
                       getBizPair('2655 El Camino Real', 'costco'),
                       getBizPair('435 w. katella ave', 'home depot'),
                       getBizPair('23651 El Toro rd', 'home depot'),
                       getBizPair('more saving','home depot'),
                       getBizPair('1288 Camino Del Rio N', 'target'),
                       getBizPair('test3', 'sams club'),
                       getBizPair('pump#', 'sams gas'),
                       getBizPair('test5', 'blu'),
                       getBizPair('farmers market', 'sprouts'),
                       getBizPair('wyndham', 'worldmark'),
                       getBizPair('CROWN ACE', 'ace'),
                       getBizPair('ralphs', 'ralphs'),
                       getBizPair('best buy', 'best buy'),
                       getBizPair('walmart', 'walmart'),
                       getBizPair('cvs', 'cvs'),
                       getBizPair('gate market', 'northgate'),
                       getBizPair('mother', 'mothers'),
                       getBizPair('albertsons', 'albertsons'),
                       getBizPair('& state college', '99c'),
                       getBizPair('Garden Grove #126', 'costco'),
                       getBizPair('homedepot', 'home depot'),
                       getBizPair('309 lake forest', '99c'),
                       getBizPair('car wash', 'carwash'),
                       getBizPair('starbucks', 'starbucks'),
                       getBizPair('389 lake forest', '99c'),
                       getBizPair('789 south tustin', '99c'),
                       getBizPair('more saving', 'home depot'),
                       getBizPair('low prices.*every day', 'walmart'),
                       getBizPair('24952 raymond way', 'usps'),
                       getBizPair('11000 Garden', 'costco'),
                       getBizPair('wholesale', 'costco'),
                       getBizPair('dunkin', 'dunkin'),
                       getBizPair('115 Technology Drive', 'costco')]

    business_name = None

    modified_search_list = []
    for x in receipt_in_list:
        modified_search_list.append(x.lower())

    for d in search_list_dic:
        search_item = d['search_item']
        search_bizname = d['bizname']

        r_search_item = re.compile(".*" + search_item)
        r_bizname = re.compile(search_bizname)

        list_search_item = list(filter(r_search_item.match, modified_search_list))
        list_bizname = list(filter(r_bizname.match, modified_search_list))

        if list_bizname:
            business_name = search_bizname
            break

        if list_search_item:
            business_name = search_bizname
            break

    if business_name is None:
        business_name = "unknown biz"

    return business_name


def __getValidDate(string_date):

    result = re.search("[JFMASOND][a-zA-Z]{3,8}[ ]+", string_date)

    month = 0
    year = 0
    day = 0

    if result is not None:

        month_string = result.group()

        month_key = month_string[0:3].capitalize()

        month_dict = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                      'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                      'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

        month = month_dict[month_key]

        day_year = string_date.replace(month_string, "")

        day = int(re.search("[0-9]{1,2}[,][ ]+", day_year).group().replace(", ", ""))

        year = int(re.search("20[0-9]{2}", day_year).group())

    else:

        if string_date.find('/') != -1:
            split_char = '/'
        else:
            split_char = '-'

        date_list = string_date.split(split_char)

        if len(date_list) == 3:

            month = int(date_list[0])
            day = int(date_list[1])
            year = int(date_list[2])
            if 0 <= year <= 99:
                year = 2000 + year

    if 1 <= month <= 12 and \
        1 <= day <= 31 and  \
        2019 <= year <= 2020:

        return datetime.date(year, month, day)

    return None


def getDate(receipt_in_list):
    """
    get biz receipt date using receipt list passed as parameter.

        \param receipt_in_list: list that contains receipt content.  Each line is contained in an item.

        \return text string with date in format YYYY-MM-DD, e.g., 2019-02-08.
    """

    date_set = set()

    for item in receipt_in_list:
        result = re.search("[0-9]{1,2}[/-][0-9]{1,2}[/-](20)?[0-9]{2}", item)

        if result is None:
            result = re.search("[JFMASOND][a-zA-Z]{3,8}[ ]+[0-9]{1,2}[,][ ]+20[0-9]{2}", item)

        if result is not None:
            actual_date = __getValidDate(result.group())
            if actual_date is not None:
                date_set.add(actual_date)
                break

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

    std_list = standard_file.lower().split("-")
    auto_list = automatic_file.lower().split("-")

    std_date = std_list[0] + "-" + std_list[1] + "-" + std_list[2]
    auto_date = auto_list[0] + "-" + auto_list[1] + "-" + auto_list[2]

    if std_date == auto_date:
        results["date equal"] = 1

    if std_list[3] == auto_list[3]:
        results["name equal"] = 1

    std_price = std_list[4].split(".pdf")
    auto_price = auto_list[4].split(".pdf")

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

        if __file.count('-') != 4:
            continue

        __text_file = getReceipt(__file)

        __list_file = __text_file.split("\n")


        __the_filename = getFilename(__list_file) + ".pdf"

        compare_results = compare_filenames(__file, __the_filename)

        result_list.append(compare_results)

        if(compare_results['date equal'] == 0 or
           compare_results['name equal'] == 0 or
           compare_results['price equal'] == 0):

            print(__list_file)
            print(compare_results)
            print("")

    print("\n"+match_results_summary(result_list))