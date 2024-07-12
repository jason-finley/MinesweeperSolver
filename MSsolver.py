from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def getClass(driver, r, c):
    # Get the class attribute of a tile element identified by its row (r) and column (c)
    tile = driver.find_element(By.ID, str(r) + "_" + str(c))
    tile_cond = tile.get_attribute("class")
    return tile_cond

def list_surrroundings(driver, r, c, cond):
    # List the surrounding tiles' classes around the tile at position (r, c)
    surs = []

    # Above row
    if r != 1:
        if c != 1:
            surs.append(getClass(driver, r - 1, c - 1))
        else:
            surs.append("")
        surs.append(getClass(driver, r - 1, c))
        if c != 30:
            surs.append(getClass(driver, r - 1, c + 1))
        else:
            surs.append("")
    else:
        surs.extend(["", "", ""])

    # Same row
    if c != 1:
        surs.append(getClass(driver, r, c - 1))
    else:
        surs.append("")
    surs.append(cond)  # middle tile
    if c != 30:
        surs.append(getClass(driver, r, c + 1))
    else:
        surs.append("")

    # Below row
    if r != 16:
        if c != 1:
            surs.append(getClass(driver, r + 1, c - 1))
        else:
            surs.append("")
        surs.append(getClass(driver, r + 1, c))
        if c != 30:
            surs.append(getClass(driver, r + 1, c + 1))
        else:
            surs.append("")
    else:
        surs.extend(["", "", ""])

    return surs

def det_surs(driver, tile_cond, surs, r, c):
    # Determine actions based on tile conditions and surrounding tiles
    blanks = surs.count("square blank")
    flags = surs.count("square bombflagged")
    action = False

    if blanks != 0:
        # Check if all surrounding bombs are flagged
        if tile_cond == blanks + flags:
            for i in range(blanks):
                index = surs.index("square blank")
                bomb_r = int(index / 3) - 1
                bomb_c = (index % 3) - 1
                print("FLAG:", r + bomb_r, c + bomb_c)
                bomb_tile = driver.find_element(By.ID, str(r + bomb_r) + "_" + str(c + bomb_c))
                ActionChains(driver).context_click(bomb_tile).perform()
                surs[index] = "square bombflagged"
                if bomb_r == -1:
                    action = True

        # Check if all surrounding bombs are correctly flagged
        if tile_cond == flags:
            for i in range(blanks):
                index = surs.index("square blank")
                safe_r = int(index / 3) - 1
                safe_c = (index % 3) - 1
                print("CLICK:", r + safe_r, c + safe_c)
                safe_tile = driver.find_element(By.ID, str(r + safe_r) + "_" + str(c + safe_c))
                safe_tile.click()
                surs[index] = "square open"
                if safe_c == -1:
                    action = True

    return action

def game(driver):
    # Main game logic
    tile1 = driver.find_element(By.ID, "1_1")
    tile1.click()

    face = driver.find_element(By.ID, "face")
    face_shape = face.get_attribute("class")

    r = 1
    c = 1
    full_col = True
    empty_cols = True
    lower = 1
    run_cols = []
    empty_cols = []
    for i in range(30):
        run_cols.append(int(i + 1))
        empty_cols.append(False)

    index = 0
    while face_shape != "facedead":
        c = run_cols[index]
        tile = driver.find_element(By.ID, str(r) + "_" + str(c))
        tile_cond = tile.get_attribute("class")

        if tile_cond == "square blank":
            empty_cols[run_cols[index] - 1] = False

        if tile_cond != "square blank" and tile_cond != "square open0" and tile_cond != "square bombflagged":
            surs = list_surrroundings(driver, r, c, tile_cond[11])
            action = det_surs(driver, eval(tile_cond[11]), surs, r, c)
            if action:
                r = 0
                if index != 0:
                    index -= 1
                else:
                    index = 0
            else:
                full_col = False

        if r == 16:
            if full_col:
                index = -1
            elif index != 0:
                if empty_cols[index - 1] and empty_cols[index] and empty_cols[index + 1]:
                    if index + 1 in run_cols:
                        run_cols.remove(index + 1)
            elif run_cols[index] == 1 and empty_cols[index] and empty_cols[index + 1]:
                run_cols.remove(run_cols[0])

            r = 0
            full_col = True
            index += 1

            if index > len(run_cols) - 1:
                index = 0

            print(index, run_cols)
            print(index, empty_cols)

            empty_cols[index] = True

        r += 1

        face = driver.find_element(By.ID, "face")
        face_shape = face.get_attribute("class")

    print("GAME OVER")

def main():
    # Main function to initialize driver and start the game loop
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://minesweeperonline.com/")

    while True:
        input("Ready...?")
        game(driver)

main()
