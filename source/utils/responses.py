from anilibria import TitleEpisode, Title


new_episode_template = """**{name}**
Новая серия: {episode}
"""


def title_episode_text(event: TitleEpisode) -> str:
    text: str = new_episode_template.format(
        name=event.title.names.ru,
        episode=event.episode.episode
    )
    return text
