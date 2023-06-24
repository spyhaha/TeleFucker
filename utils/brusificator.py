import random


def text_with_cyrillic_characters_obfuscated(text, hard=True):
    """
        Брусификатор сообщения от крини
        Заменяет кирилицу на схожие юникод аналоги
    """

    cyrillic_obfuscation_mapping = {
        # 'cyrillic': 'obfuscated',
        'а': 'a',
        'А': 'A𝖠',
        'Б': 'ƃ',
        'в': 'ⲃ',
        'В': 'B',  # βß
        'Г': 'Γ',
        # 'Д'
        'е': 'e𝚎',  # ēėěêéè
        'Е': 'EΕ',
        # 'ж': 'җ',
        # 'Ж': 'Җ',
        # 'З': '3',
        # 'и': 'ͷ',  # ͷ sucks on phone
        # 'И': 'Ͷ',  # Ͷ sucks on phone
        # 'й'
        'к': 'κⲕ',
        'К': 'K',  # Ҝ
        # 'л'
        # 'м': 'ʍ',
        'М': 'M𝖬',
        # 'н': 'ʜ',
        'Н': 'HН',
        'о': 'o',
        'О': 'O𝖮',
        # 'п': 'nn',
        'П': 'Π',
        'р': 'p',  # ƿ
        'Р': 'P',
        'с': 'c',
        'С': 'C',
        'Т': 'TT',  # Ͳ
        'у': 'y',
        'У': 'Ꭹ',
        'ф': 'Փ',
        'Ф': 'Φ',
        'х': 'xⲭ',
        'Х': 'XⲬ',
        # 'ц'
        #
        # 'ч'
        #
        # 'ш'
        #
        # 'щ'
        #
        # 'ы'
        #
        # 'Э': '℈',
        #
        # 'ю'
        #
        # 'я'
    }

    def can_be_obfuscated(character):
        return character in cyrillic_obfuscation_mapping

    def obfuscation_options(character) -> list:
        if hard:
            return list(cyrillic_obfuscation_mapping[character])
        else:
            return list(cyrillic_obfuscation_mapping[character][0])

    def obfuscated_character(character):
        return random.choice(obfuscation_options(character))

    obfuscated_message = ''

    for ch in text:
        if can_be_obfuscated(ch) and random.randint(0, 1) == 0:
            obfuscated_message += obfuscated_character(ch)
        else:
            obfuscated_message += ch

    return obfuscated_message
