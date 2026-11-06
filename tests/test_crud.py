"""Unit tests for MongoDB CRUD behavior without a running database."""
import os
import unittest
from unittest.mock import MagicMock, patch

from crud import AnimalShelter


class AnimalShelterTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.collection = self.client.__getitem__.return_value.__getitem__.return_value
        self.shelter = AnimalShelter(client=self.client)

    def test_requires_connection_setting(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "MONGO_URI"):
                AnimalShelter()

    def test_create_acknowledged(self):
        self.collection.insert_one.return_value.acknowledged = True
        self.assertTrue(self.shelter.create({"animal_id": "A1"}))
        self.collection.insert_one.assert_called_once_with({"animal_id": "A1"})

    def test_rejects_empty_create(self):
        with self.assertRaises(ValueError):
            self.shelter.create({})

    def test_read_accepts_default_empty_filter(self):
        self.collection.find.return_value = [{"animal_id": "A1"}]
        self.assertEqual(self.shelter.read(), [{"animal_id": "A1"}])
        self.collection.find.assert_called_once_with({})

    def test_read_rejects_non_mapping(self):
        with self.assertRaises(TypeError):
            self.shelter.read("everything")

    def test_update_uses_set_operator(self):
        self.collection.update_many.return_value.modified_count = 2
        result = self.shelter.update({"animal_type": "Dog"}, {"status": "reviewed"})
        self.assertEqual(result, 2)
        self.collection.update_many.assert_called_once_with(
            {"animal_type": "Dog"}, {"$set": {"status": "reviewed"}}
        )

    def test_update_rejects_unfiltered_writes(self):
        with self.assertRaises(ValueError):
            self.shelter.update({}, {"status": "reviewed"})
        with self.assertRaises(ValueError):
            self.shelter.update({"animal_id": "A1"}, {})

    def test_delete_rejects_unfiltered_deletes(self):
        with self.assertRaises(ValueError):
            self.shelter.delete({})

    def test_delete_returns_deleted_count(self):
        self.collection.delete_many.return_value.deleted_count = 1
        self.assertEqual(self.shelter.delete({"animal_id": "A1"}), 1)


if __name__ == "__main__":
    unittest.main()
