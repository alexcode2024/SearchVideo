from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_video_description(driver, video_url):
    """获取视频页面的详细描述"""
    try:
        # 保存当前窗口句柄
        current_window = driver.current_window_handle
        
        # 在新标签页中打开视频
        driver.execute_script(f"window.open('{video_url}', '_blank');")
        time.sleep(1)
        
        # 切换到新标签页
        driver.switch_to.window(driver.window_handles[-1])
        
        # 等待并获取描述信息
        try:
            desc = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "desc-info-text"))
            ).text
        except:
            desc = "暂无描述"
        
        # 关闭当前标签页
        driver.close()
        
        # 切回原标签页
        driver.switch_to.window(current_window)
        
        return desc
        
    except Exception as e:
        print(f"获取视频描述时出错: {str(e)}")
        # 确保切回原标签页
        driver.switch_to.window(current_window)
        return "获取描述失败"

def process_keyword(driver, keyword):
    """处理单个关键词的搜索"""
    try:
        print(f"\n正在搜索关键词: {keyword}")
        
        # 等待搜索框可点击
        search_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "nav-search-input"))
        )
        
        # 先点击搜索框
        search_box.click()
        
        # 多重清除搜索框内容
        search_box.clear()
        # 使用 Ctrl+A 全选并删除
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.DELETE)
        # 再次清除确保干净
        search_box.clear()
        
        # 检查搜索框是否为空
        current_text = search_box.get_attribute('value')
        if current_text:
            print(f"警告：搜索框未完全清空，当前内容：{current_text}")
            # 再次尝试清空
            search_box.clear()
            search_box.send_keys(Keys.CONTROL + "a", Keys.DELETE)
        
        # 输入搜索关键词
        search_box.send_keys(keyword)
        time.sleep(1)
        
        # 点击搜索按钮
        search_button = driver.find_element(By.CLASS_NAME, "nav-search-btn")
        search_button.click()
        time.sleep(1)
        
        # 切换到新标签页
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            
        # 获取并保存视频信息
        videos = get_video_list(driver)
        if videos:
            save_results(videos, keyword)
            
        # 关闭当前搜索结果标签页，回到主页
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            
    except Exception as e:
        print(f"处理关键词 '{keyword}' 时出错: {str(e)}")
        # 确保回到主页面
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[0])

def get_video_list(driver):
    """获取视频列表"""
    try:
        video_items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "bili-video-card"))
        )
        
        if not video_items:
            print("未找到任何视频")
            return None
            
        if len(video_items) < 10:
            print(f"警告：只找到 {len(video_items)} 个视频，少于预期的10个")
            
        print(f"找到 {len(video_items)} 个视频")
        
        videos = []
        processed_count = 0
        
        for item in video_items:
            if processed_count >= 10:
                break
                
            try:
                video_link = item.find_element(By.TAG_NAME, "a")
                link = video_link.get_attribute("href")
                title = item.find_element(By.CSS_SELECTOR, ".bili-video-card__info--tit").text
                
                print(f"获取第{processed_count + 1}个视频信息:")
                print(f"标题: {title}")
                print(f"链接: {link}")
                
                if not link or not isinstance(link, str):
                    print(f"跳过无效链接: {link}")
                    continue
                
                if not link.startswith("https://www.bilibili.com/video/"):
                    print(f"跳过非视频链接: {link}")
                    continue
                
                print(f"正在获取视频描述...")
                desc = get_video_description(driver, link)
                
                videos.append({
                    'title': title,
                    'description': desc,
                    'url': link
                })
                
                processed_count += 1
                print(f"已处理 {processed_count} 个视频")
                
            except Exception as e:
                print(f"获取第{processed_count + 1}个视频信息时出错: {str(e)}")
                continue
                
        return videos
        
    except Exception as e:
        print(f"获取视频列表时出错: {str(e)}")
        return None

def save_results(videos, keyword):
    """保存搜索结果到文件"""
    filename = "bilibili_search_result.txt"
    print(f"正在保存{len(videos)}个视频的信息到 {filename}...")
    
    # 使用追加模式打开文件
    with open(filename, "a", encoding="utf-8") as f:
        # 写入关键词分隔标记
        f.write("\n")
        f.write("=" * 50 + "\n")
        f.write(f"搜索关键词: {keyword}\n")
        f.write("=" * 50 + "\n\n")
        
        # 写入视频信息
        for index, video in enumerate(videos, 1):
            print(f"保存第{index}个视频信息...")
            f.write(f"视频 {index}:\n")
            f.write(f"标题: {video['title']}\n")
            f.write(f"描述: {video['description']}\n")
            f.write(f"链接: {video['url']}\n")
            f.write("-" * 50 + "\n")
        
        # 在每个关键词的结果后添加额外的分隔行
        f.write("\n")

def main():
    # 读取关键词文件
    try:
        with open("keywords.txt", "r", encoding="utf-8") as f:
            keywords = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"读取关键词文件时出错: {str(e)}")
        return
        
    if not keywords:
        print("未找到任何关键词")
        return
        
    print(f"读取到 {len(keywords)} 个关键词")
    
    # 清空结果文件
    with open("bilibili_search_result.txt", "w", encoding="utf-8") as f:
        f.write("B站视频搜索结果\n")
        f.write("=" * 50 + "\n")
        f.write(f"搜索时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
    
    # 设置浏览器选项
    options = webdriver.EdgeOptions()
    options.add_argument('--disable-gpu')  # 禁用GPU加速
    options.add_argument('--no-sandbox')   # 禁用沙箱模式
    options.add_argument('--disable-dev-shm-usage')  # 禁用/dev/shm使用
    options.add_argument('--disable-software-rasterizer')  # 禁用软件光栅化
    options.add_argument('--ignore-certificate-errors')  # 忽略证书错误
    options.add_argument('--disable-extensions')  # 禁用扩展
    options.add_argument('--disable-webgl')  # 禁用WebGL
    options.add_argument('--disable-notifications')  # 禁用通知
    options.add_argument('--log-level=3')  # 只显示重要的日志信息
    
    # 创建浏览器实例
    driver = webdriver.Edge(options=options)
    
    try:
        # 打开B站
        print("正在打开B站...")
        driver.get("https://www.bilibili.com/")
        time.sleep(3)
        
        # 处理每个关键词
        for keyword in keywords:
            process_keyword(driver, keyword)
            
    except Exception as e:
        print(f"发生错误: {str(e)}")
    
    finally:
        print("\n所有关键词处理完成，正在关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    main() 