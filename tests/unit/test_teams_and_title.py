from teams import Teams
from title import Title


def test_every_team_has_menu_and_ingame_image():
    for team in Teams:
        menu_image, ingame_image = team.value
        assert menu_image.endswith(".png")
        assert ingame_image.endswith("_ingame.png")


def test_show_title_lists_all_hotkeys(capsys):
    Title.show_title()
    output = capsys.readouterr().out

    for text in ("Wardogs Team Auto Picker", "F1 for Lonestar", "F2 for Valkyra", "F3 for Manticore", "ESC"):
        assert text in output
