supported_bots = [
    "console",
    "lookup",
]


def run_bot(bot):
    if bot not in supported_bots:
        bot = "console"

    if bot == "console":
        from ..bots.console import ConsoleBot

        ConsoleBot().start()
    elif bot == "lookup":
        from ..bots.lookup import LookupBot

        LookupBot().start()
    else:
        print("Unknown bot: %s" % bot)
