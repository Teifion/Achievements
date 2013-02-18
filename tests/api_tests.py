"""
The idea is to use this file for working on a new test and getting the answer right away.
"""

import transaction
from . import test_lib
from ..config import config
from .. import api

from ..achievement_models import (
    AchievementCategory,
)

class APITest(test_lib.DBTestClass):
    def test_registration(self):
        with transaction.manager:
            config['DBSession'].execute("DELETE FROM achievement_categories WHERE name LIKE '_TEST_%'")
            config['DBSession'].execute("COMMIT")
        
        results = list(config['DBSession'].query(AchievementCategory).filter(AchievementCategory.name.like("ATEST_%")))
        self.assertEqual(results, [], "\
We were unable to successfully remove all achievement categories. We cannot\
 correctly test the ability to register achievement categories.")
        
        # Insert
        api.register_category_tree([
            "ATEST_TestCat1", [
                "_ATEST_Sub1", ["_ATEST_Sub1_Sub1", "_ATEST_Sub1_Sub2"],
                "ATEST_Sub2", ["ATEST_Sub2_Sub1", "ATEST_Sub2_Sub2"],
            ]
        ])
        
        repr_category = lambda c: (c.name, c.private, c.id, c.parent)
        
        # Now check it's gone in correctly
        results = map(
            repr_category,
            config['DBSession'].query(AchievementCategory).filter(AchievementCategory.name.like("_TEST_%")).order_by(AchievementCategory.id.asc())
        )
        
        expected_results = (
            ('ATEST_TestCat1', False),
            ('ATEST_Sub1', True),
            ('ATEST_Sub1_Sub1', True),
            ('ATEST_Sub1_Sub2', True),
            ('ATEST_Sub2', False),
            ('ATEST_Sub2_Sub1', False),
            ('ATEST_Sub2_Sub2', False),
        )
        
        for i, r in enumerate(results):
            er = expected_results[i]
            
            # Test name and private
            self.assertEqual(er[0], r[0])
            self.assertEqual(er[1], r[1])
        
        # TODO: Test parent property
