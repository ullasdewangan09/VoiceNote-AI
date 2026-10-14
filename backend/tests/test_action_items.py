from app.services.action_item_service import ActionItemService


def test_detect_action_item_with_owner_and_deadline():
    """Verify action item detection extracts task, owner, and deadline."""
    text = "Rahul needs to prepare the deployment documentation by Friday."
    items = ActionItemService.detect_action_items(text)
    
    assert len(items) == 1
    item = items[0]
    assert "prepare the deployment documentation" in item["task"].lower()
    assert item["owner"] == "Rahul"
    assert item["deadline"] == "Friday"
    assert item["source_sentence"] == text


def test_detect_action_item_without_owner_and_deadline():
    """Verify non-hallucination rule: owner and deadline are None when not specified."""
    text = "We need to update the configuration file."
    items = ActionItemService.detect_action_items(text)
    
    assert len(items) == 1
    item = items[0]
    assert "update the configuration file" in item["task"].lower()
    assert item["owner"] is None or item["owner"] in {"We", "we"}
    assert item["deadline"] is None


def test_detect_action_item_no_matches():
    """Verify statements without action triggers yield 0 action items."""
    text = "The weather was sunny yesterday during the team lunch."
    items = ActionItemService.detect_action_items(text)
    assert len(items) == 0
