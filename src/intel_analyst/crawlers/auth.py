"""
爬虫认证模块 —— 处理需要登录的站点。

authenticate_requests(): requests 模式的表单提交登录，返回带 cookie 的 Session。
login_with_selenium():   selenium 模式，用 headless Chrome 模拟浏览器登录，
                         提取 cookie 后注入 requests.Session。

被 GenericNewsCrawler._create_session() 调用，根据 AuthConfig.mode 选择认证方式。
"""

import os
from dataclasses import dataclass

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from intel_analyst.schemas.source import AuthConfig


@dataclass
class SessionAuthResult:
    session: requests.Session


def authenticate_requests(auth: AuthConfig) -> SessionAuthResult:
    session = requests.Session()
    if auth.mode == "none":
        return SessionAuthResult(session=session)

    if auth.mode != "requests":
        return SessionAuthResult(session=session)

    if not auth.login_url or not auth.username_env or not auth.password_env:
        return SessionAuthResult(session=session)

    username = os.getenv(auth.username_env, "")
    password = os.getenv(auth.password_env, "")
    payload = {"username": username, "password": password}
    session.post(str(auth.login_url), data=payload, timeout=20)
    return SessionAuthResult(session=session)


def login_with_selenium(auth: AuthConfig) -> requests.Session:
    session = requests.Session()
    if auth.mode != "selenium":
        return session

    if not all(
        [
            auth.login_url,
            auth.username_env,
            auth.password_env,
            auth.username_selector,
            auth.password_selector,
            auth.submit_selector,
            auth.success_selector,
        ]
    ):
        return session

    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    username = os.getenv(auth.username_env, "")
    password = os.getenv(auth.password_env, "")

    try:
        driver.get(str(auth.login_url))
        WebDriverWait(driver, auth.timeout_seconds).until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, auth.username_selector))
        )
        driver.find_element(By.CSS_SELECTOR, auth.username_selector).send_keys(username)
        driver.find_element(By.CSS_SELECTOR, auth.password_selector).send_keys(password)
        driver.find_element(By.CSS_SELECTOR, auth.submit_selector).click()
        WebDriverWait(driver, auth.timeout_seconds).until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, auth.success_selector))
        )

        for cookie in driver.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"])
    finally:
        driver.quit()

    return session
