---
icon: lucide/layout-template
---

# Character Blueprint Service

Access read-only character sheet blueprints, including sections, categories, traits, and supernatural content that define character sheet structure.

## Usage

```python
from vclient import character_blueprint_service

blueprint = character_blueprint_service(company_id="COMPANY_ID")
```

## Methods

### Sections

Top-level organization of a character sheet (e.g., "Attributes", "Skills", "Disciplines").

| Method                                                                  | Returns                           | Description              |
| ----------------------------------------------------------------------- | --------------------------------- | ------------------------ |
| `get_sections_page(*, game_version, limit?, offset?, character_class?)` | `PaginatedResponse[SheetSection]` | Get a page of sections   |
| `list_all_sections(*, game_version, character_class?)`                  | `list[SheetSection]`              | Get all sections         |
| `iter_all_sections(*, game_version, character_class?)`                  | `AsyncIterator[SheetSection]`     | Iterate through sections |
| `get_section(*, game_version, section_id)`                              | `SheetSection`                    | Get a section by ID      |

### Categories

Nested within sections (e.g., "Physical", "Social", "Mental" within "Attributes").

| Method                                                                                | Returns                            | Description                |
| ------------------------------------------------------------------------------------- | ---------------------------------- | -------------------------- |
| `get_categories_page(*, game_version, section_id, limit?, offset?, character_class?)` | `PaginatedResponse[TraitCategory]` | Get a page of categories   |
| `list_all_categories(*, game_version, section_id, character_class?)`                  | `list[TraitCategory]`              | Get all categories         |
| `iter_all_categories(*, game_version, section_id, character_class?)`                  | `AsyncIterator[TraitCategory]`     | Iterate through categories |
| `get_category(*, game_version, section_id, category_id)`                              | `TraitCategory`                    | Get a category by ID       |

### Subcategories

Nested within categories. Not all categories have subcategories — only those with grouped traits (e.g., "Backgrounds" may have "Allies", "Resources").

| Method                                                                                                       | Returns                                | Description                    |
| ------------------------------------------------------------------------------------------------------------ | -------------------------------------- | ------------------------------ |
| `get_subcategories_page(*, game_version, section_id, category_id, limit?, offset?, character_class?)`        | `PaginatedResponse[TraitSubcategory]`  | Get a page of subcategories    |
| `list_all_subcategories(*, game_version, section_id, category_id, character_class?)`                         | `list[TraitSubcategory]`               | Get all subcategories          |
| `iter_all_subcategories(*, game_version, section_id, category_id, character_class?)`                         | `AsyncIterator[TraitSubcategory]`      | Iterate through subcategories  |
| `get_subcategory(*, game_version, section_id, category_id, subcategory_id)`                                  | `TraitSubcategory`                     | Get a subcategory by ID        |

### Subcategory Traits

Traits within a specific subcategory (requires section, category, and subcategory context).

| Method                                                                                                                                    | Returns                    | Description                              |
| ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ---------------------------------------- |
| `get_subcategory_traits_page(*, game_version, section_id, category_id, subcategory_id, limit?, offset?, character_class?)`                | `PaginatedResponse[Trait]` | Get a page of traits in a subcategory    |
| `list_all_subcategory_traits(*, game_version, section_id, category_id, subcategory_id, character_class?)`                                 | `list[Trait]`              | Get all traits in a subcategory          |
| `iter_all_subcategory_traits(*, game_version, section_id, category_id, subcategory_id, character_class?)`                                 | `AsyncIterator[Trait]`     | Iterate through subcategory traits       |

### Category Traits

Traits within a specific category (requires section and category context).

| Method                                                                                                                 | Returns                    | Description                        |
| ---------------------------------------------------------------------------------------------------------------------- | -------------------------- | ---------------------------------- |
| `get_category_traits_page(*, game_version, section_id, category_id, limit?, offset?, character_class?, character_id?, exclude_subcategory_traits?)` | `PaginatedResponse[Trait]` | Get a page of traits in a category |
| `list_all_category_traits(*, game_version, section_id, category_id, character_class?, character_id?, exclude_subcategory_traits?)`                  | `list[Trait]`              | Get all traits in a category       |
| `iter_all_category_traits(*, game_version, section_id, category_id, character_class?, character_id?, exclude_subcategory_traits?)`                  | `AsyncIterator[Trait]`     | Iterate through category traits    |

### All Traits

Search across all traits without section/category context. All parameters are optional.

!!! note "Direct Trait Access"

    Use these methods to search all traits directly without navigating the section/category hierarchy. Useful when you know what trait you're looking for but not its location in the character sheet.

| Method                                                                                                 | Returns                    | Description                |
| ------------------------------------------------------------------------------------------------------ | -------------------------- | -------------------------- |
| `get_traits_page(*, limit?, offset?, game_version?, character_class?, parent_category_id?, order_by?)` | `PaginatedResponse[Trait]` | Get a page of all traits   |
| `list_all_traits(*, game_version?, character_class?, parent_category_id?, order_by?)`                  | `list[Trait]`              | Get all traits             |
| `iter_all_traits(*, game_version?, character_class?, parent_category_id?, order_by?)`                  | `AsyncIterator[Trait]`     | Iterate through all traits |
| `get_trait(*, trait_id)`                                                                               | `Trait`                    | Get a trait by ID          |

### Character Concepts

| Method                                  | Returns                               | Description              |
| --------------------------------------- | ------------------------------------- | ------------------------ |
| `get_concepts_page(*, limit?, offset?)` | `PaginatedResponse[CharacterConcept]` | Get a page of concepts   |
| `list_all_concepts()`                   | `list[CharacterConcept]`              | Get all concepts         |
| `iter_all_concepts()`                   | `AsyncIterator[CharacterConcept]`     | Iterate through concepts |
| `get_concept(*, concept_id)`            | `CharacterConcept`                    | Get a concept by ID      |

### Vampire Clans

| Method                                                      | Returns                          | Description           |
| ----------------------------------------------------------- | -------------------------------- | --------------------- |
| `get_vampire_clans_page(*, limit?, offset?, game_version?)` | `PaginatedResponse[VampireClan]` | Get a page of clans   |
| `list_all_vampire_clans(*, game_version?)`                  | `list[VampireClan]`              | Get all clans         |
| `iter_all_vampire_clans(*, game_version?)`                  | `AsyncIterator[VampireClan]`     | Iterate through clans |
| `get_vampire_clan(*, vampire_clan_id)`                      | `VampireClan`                    | Get a clan by ID      |

### Werewolf Tribes

| Method                                                        | Returns                            | Description            |
| ------------------------------------------------------------- | ---------------------------------- | ---------------------- |
| `get_werewolf_tribes_page(*, limit?, offset?, game_version?)` | `PaginatedResponse[WerewolfTribe]` | Get a page of tribes   |
| `list_all_werewolf_tribes(*, game_version?)`                  | `list[WerewolfTribe]`              | Get all tribes         |
| `iter_all_werewolf_tribes(*, game_version?)`                  | `AsyncIterator[WerewolfTribe]`     | Iterate through tribes |
| `get_werewolf_tribe(*, werewolf_tribe_id)`                    | `WerewolfTribe`                    | Get a tribe by ID      |

### Werewolf Auspices

| Method                                                          | Returns                              | Description              |
| --------------------------------------------------------------- | ------------------------------------ | ------------------------ |
| `get_werewolf_auspices_page(*, limit?, offset?, game_version?)` | `PaginatedResponse[WerewolfAuspice]` | Get a page of auspices   |
| `list_all_werewolf_auspices(*, game_version?)`                  | `list[WerewolfAuspice]`              | Get all auspices         |
| `iter_all_werewolf_auspices(*, game_version?)`                  | `AsyncIterator[WerewolfAuspice]`     | Iterate through auspices |
| `get_werewolf_auspice(*, werewolf_auspice_id)`                  | `WerewolfAuspice`                    | Get an auspice by ID     |

## Example

```python
# List all sections for V5
sections = await blueprint.list_all_sections(game_version="V5")

for section in sections:
    print(f"Section: {section.name}")

    # Get categories within this section
    categories = await blueprint.list_all_categories(
        game_version="V5",
        section_id=section.id
    )

    for category in categories:
        print(f"  Category: {category.name}")

        # Get top-level traits (excluding subcategory traits)
        traits = await blueprint.list_all_category_traits(
            game_version="V5",
            section_id=section.id,
            category_id=category.id,
            exclude_subcategory_traits=True,
        )

        for trait in traits:
            print(f"    Trait: {trait.name}")

        # Get subcategories within this category
        subcategories = await blueprint.list_all_subcategories(
            game_version="V5",
            section_id=section.id,
            category_id=category.id,
        )

        for subcategory in subcategories:
            print(f"    Subcategory: {subcategory.name}")

            # Get traits within this subcategory
            sub_traits = await blueprint.list_all_subcategory_traits(
                game_version="V5",
                section_id=section.id,
                category_id=category.id,
                subcategory_id=subcategory.id,
            )

            for trait in sub_traits:
                print(f"      Trait: {trait.name}")

# Search all traits directly
all_traits = await blueprint.list_all_traits(game_version="V5")
```

See [Response Models](../models/character_blueprint.md) for `SheetSection`, `TraitCategory`, `TraitSubcategory`, `Trait`, and related types.
