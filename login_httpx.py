import requests, json
import time
import re
import httpx

url = "https://distributors.iaiquality.com/"

# ============ STEP 1: LOGIN REQUEST ============
login_data = {
    "swpm_login_origination_flag": "1",
    "swpm_user_name": "dnguyen@valin.com",
    "swpm_password": "123456",
    "swpm-login": "Log In",
}

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://distributors.iaiquality.com",
    "Referer": "https://distributors.iaiquality.com/",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

print("[*] Starting login flow...")
print("[*] Step 1: Sending login credentials...")

with httpx.Client() as s:
    # Warm up session
    s.get(url, headers=headers, timeout=30)

    # Step 1: Send login request
    # Note: Don't pass cookies manually when using Session - let it manage cookies automatically
    resp1 = s.post(
        url,
        headers=headers,
        data=login_data,
        timeout=30,
    )

    print(f"[✓] Login response status: {resp1.status_code}")
    print(f"[✓] Redirected to: {resp1.url}")
    
    # Check if 2FA page is shown (optional - helps verify we got to 2FA step)
    if "2fa" in resp1.text.lower() or "two-factor" in resp1.text.lower():
        print("[✓] 2FA page detected!")
    
    # ============ STEP 2: PAUSE AND GET 2FA CODE FROM USER ============
    print("\n" + "="*60)
    print("[!] A 2FA code has been sent to your email/phone")
    print("[!] Check your email or authenticator app")
    print("="*60 + "\n")
    
    # Pause and wait for user input
    time.sleep(2)  # Small pause before prompting
    twofa_code = input("➜ Enter your 2FA code: ").strip()
    
    if not twofa_code:
        print("[✗] Error: 2FA code cannot be empty!")
        exit(1)
    
    print(f"[✓] 2FA code received: {twofa_code}\n")
    
    # ============ STEP 3: SUBMIT 2FA CODE ============
    print("[*] Step 2: Submitting 2FA code...")
    
    twofa_data = {
        "swpm_login_origination_flag": "1",
        "swpm_user_name": "dnguyen@valin.com",
        "swpm_password": "123456",
        "swpm_2fa_code": twofa_code,  # Use the user-provided code
        "swpm_2fa_submit": "Continue",
    }
    
    # Note: The session will have updated cookies from the first request
    resp2 = s.post(
        url,
        headers=headers,
        data=twofa_data,
        timeout=30,
    )

    print(f"[✓] 2FA response status: {resp2.status_code}")
    print(f"[✓] URL: {resp2.url}")
    print(f"\n[✓] Login flow completed!")
    
    # ============ CAPTURE COOKIES ============
    print("\n" + "="*60)
    print("[*] Captured Cookies from resp2:")
    print("="*60)
    
    # Get cookies from the session, handling potential duplicates
    try:
        extract_cookies = {cookie.name: cookie.value for cookie in s.cookies.jar}
        
    except Exception:
        # If there are conflicting cookies, iterate through them instead
        print("[!] Warning: Multiple cookies with same name detected. Listing all cookies:")
    
    print("="*60)
    
    # ============ STEP 4: GET PRICING PAGE AND EXTRACT NONCE ============
    print("\n[*] Step 3: Fetching pricing page...")
    
    pricing_url = "https://distributors.iaiquality.com/iai-product-model-and-price-check/"
    resp3 = s.get(pricing_url, headers=headers, timeout=30)
    
    print(f"[✓] Pricing page status: {resp3.status_code}")
    
    # Use regex to find the nonce value in RAPROS_PRICING variable
    pattern = r'var\s+RAPROS_PRICING\s*=\s*\{[^}]*"nonce":"([^"]+)"'
    match = re.search(pattern, resp3.text)
    
    if match:
        nonce = match.group(1)
        print(f"\n[✓] Nonce extracted successfully!")
        print(f"[*] Nonce value: {nonce}")
        extract_cookies['x-wp-nonce'] = nonce  # Add nonce to cookies dict

    with open("cookies.json", "w") as f:
            json.dump(extract_cookies, f, indent=4)

