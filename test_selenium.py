from selenium import webdriver

driver = webdriver.Edge()
driver.get("https://www.baidu.com")
print("浏览器启动成功！")
driver.quit() 