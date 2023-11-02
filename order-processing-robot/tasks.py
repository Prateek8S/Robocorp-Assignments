from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(slowmo=120)
    open_robot_order_website()
    download_orders_data()
    order_robot()
    archive_receipts()


""" Open the Website """
def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

""" Download the csv File """
def download_orders_data():
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", "./output/orders.csv", overwrite=True)


""" Read the Data """
def get_orders():
    tables = Tables()
    orders_data = tables.read_table_from_csv(path="./output/orders.csv", header=True)
    return orders_data




""" Close the Modal on the Webpage"""
def close_annoying_modal():
    try:
        page = browser.page()
        page.click('//div[@class="alert-buttons"]/button[text()="OK"]')
    except Exception as e:
        # Handle any exceptions
        print(f"An error occurred: {str(e)}")




""" Fill The Form"""
def fill_the_form(order):
    page = browser.page()

    page.select_option('#head', order["Head"])
    page.click('//input[@value=' + order["Body"] + ']')
    page.fill('//label[text()="3. Legs:"]/ancestor::div/input', order["Legs"])
    page.fill('#address', order["Address"])
    page.click("#preview")
    page.click("#order")

    handle_error()




""" Store Receipt as  PDF """
def store_receipt_as_pdf(order_number):
    
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(receipt_html, "./output/receipts/" + order_number + " receipt.pdf")
    return "./output/receipts/" + order_number + " receipt.pdf"



"""Take a Screenshot of the Preview"""
def screenshot_robot(order_number):
    
    page = browser.page()
    page.locator("#robot-preview-image").screenshot(path="./output/roboimage/robo_" + order_number + ".png")
    return "./output/roboimage/robo_" + order_number + ".png"





""" Attach Screenshot to Receipt """
def attach_screenshot_to_receipt(screenshot, pdf_file):

    pdf = PDF()
    pdf.add_files_to_pdf(files=[pdf_file, screenshot], target_document=pdf_file)



""" Order Another Robot """
def order_another_robot():
    
    page = browser.page()
    order_new_robot = page.locator("#order-another")
    page.click('#order-another')




""" Archive the Receipts """
def archive_receipts():
    
    archive = Archive()
    archive.archive_folder_with_zip(folder="./output/receipts", archive_name="./output/receipts.zip")



""" THE ITERATION """
def order_robot():
    data = get_orders()
    for order in data:
        
        close_annoying_modal()
        fill_the_form(order)

        receipt_pdf_path = store_receipt_as_pdf(order["Order number"])
        screenshot_path = screenshot_robot(order["Order number"])
        attach_screenshot_to_receipt(screenshot_path, receipt_pdf_path)
        order_another_robot()
                


""" Handle Submit Error """
def handle_error():
    page = browser.page()
    # error_pop_up = page.locator('//div[@class="alert alert-danger"]')
    element = page.query_selector('//div[@class="alert alert-danger"]')
    if element:
        for i in range(100):
            element = page.query_selector('//div[@class="alert alert-danger"]')
            if element:
                alert_text = element.inner_text()
                print(alert_text)
                page.click("#order")
            else:
                break
    else:
        print("No alert found")
        


