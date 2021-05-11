from agents import Bot
import time

BOT_1_JID = "test_agent@jabbim.pl/111"
BOT_2_JID = "test_agent@jabbim.pl/222"
BOT_3_JID = "test_agent@jabbim.pl/333"


if __name__ == "__main__":
    bot1 = Bot(BOT_1_JID, '123', '{1,1}', [BOT_2_JID, BOT_3_JID])
    bot1.start()

    bot2 = Bot(BOT_2_JID, '123', '{1,1}', [BOT_1_JID, BOT_3_JID])
    bot2.start()

    bot3 = Bot(BOT_3_JID, '123', '{1,1}', [BOT_1_JID, BOT_2_JID])
    bot3.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    bot1.stop()
    bot2.stop()
    bot3.stop()
