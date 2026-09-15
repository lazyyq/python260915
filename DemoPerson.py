# unittest는 프로그램이 잘 되었는지 확인하는 도구입니다.
import unittest
# 화면에 나오는 글자를 잠깐 다른 곳에 담아 두는 도구입니다.
from contextlib import redirect_stdout
# 글자를 담아 두는 작은 상자 같은 도구입니다.
from io import StringIO


class Person:
    # Person은 사람 한 명을 나타내는 설계도입니다.
    def __init__(self, id, name):
        # id는 사람에게 붙인 번호표입니다.
        self.id = id
        # name은 사람의 이름표입니다.
        self.name = name

    def printInfo(self):
        # 번호표와 이름표를 한 번에 보여 줍니다.
        print(f"ID: {self.id}, Name: {self.name}")


class Manager(Person):
    # Manager는 Person 설계도를 물려받은 관리자입니다.
    # 그래서 id와 name을 이미 가지고 있고, title도 하나 더 가집니다.
    def __init__(self, id, name, title):
        # 부모 Person에게 id와 name을 맡겨서 준비합니다.
        super().__init__(id, name)
        # title은 관리자의 직책 이름표입니다.
        self.title = title

    def printInfo(self):
        # 관리자의 번호표, 이름표, 직책을 모두 보여 줍니다.
        print(f"ID: {self.id}, Name: {self.name}, Title: {self.title}")


class Employee(Person):
    # Employee는 Person 설계도를 물려받은 직원입니다.
    # 직원은 id와 name에 더해 잘하는 일인 skill을 가집니다.
    def __init__(self, id, name, skill):
        # 부모 Person에게 공통 정보인 id와 name을 맡겨서 준비합니다.
        super().__init__(id, name)
        # skill은 직원이 잘하는 기술 이름표입니다.
        self.skill = skill

    def printInfo(self):
        # 직원의 번호표, 이름표, 기술을 모두 보여 줍니다.
        print(f"ID: {self.id}, Name: {self.name}, Skill: {self.skill}")


class TestPerson(unittest.TestCase):
    # 아래의 함수들은 작은 검사 선생님처럼 코드를 하나씩 확인합니다.
    def test_person_id(self):
        # Person의 번호표가 제대로 들어갔는지 확인합니다.
        self.assertEqual(Person(1, "Alice").id, 1)

    def test_person_name(self):
        # Person의 이름표가 제대로 들어갔는지 확인합니다.
        self.assertEqual(Person(1, "Alice").name, "Alice")

    def test_person_print_info(self):
        # 화면 대신 글자 상자에 출력 내용을 담습니다.
        output = StringIO()
        with redirect_stdout(output):
            # Person이 약속한 모양으로 글자를 출력하는지 확인합니다.
            Person(1, "Alice").printInfo()
        # 글자 상자 안의 내용이 예상한 문장과 같은지 비교합니다.
        self.assertEqual(output.getvalue().strip(), "ID: 1, Name: Alice")

    def test_manager_is_person(self):
        # Manager가 Person의 특징을 물려받았는지 확인합니다.
        self.assertIsInstance(Manager(2, "Bob", "Team Leader"), Person)

    def test_manager_title(self):
        # Manager에게 직책 이름표가 잘 붙었는지 확인합니다.
        self.assertEqual(Manager(2, "Bob", "Team Leader").title, "Team Leader")

    def test_manager_print_info(self):
        # Manager가 출력할 글자를 담아 둘 상자를 준비합니다.
        output = StringIO()
        with redirect_stdout(output):
            # 번호, 이름, 직책을 모두 보여 주는지 확인합니다.
            Manager(2, "Bob", "Team Leader").printInfo()
        # 실제 출력이 우리가 기다린 문장과 같은지 비교합니다.
        self.assertEqual(
            output.getvalue().strip(),
            "ID: 2, Name: Bob, Title: Team Leader",
        )

    def test_employee_is_person(self):
        # Employee가 Person의 특징을 물려받았는지 확인합니다.
        self.assertIsInstance(Employee(3, "Charlie", "Python"), Person)

    def test_employee_skill(self):
        # Employee에게 기술 이름표가 잘 붙었는지 확인합니다.
        self.assertEqual(Employee(3, "Charlie", "Python").skill, "Python")

    def test_employee_print_info(self):
        # Employee가 출력할 글자를 담아 둘 상자를 준비합니다.
        output = StringIO()
        with redirect_stdout(output):
            # 번호, 이름, 기술을 모두 보여 주는지 확인합니다.
            Employee(3, "Charlie", "Python").printInfo()
        # 실제 출력이 우리가 기다린 문장과 같은지 비교합니다.
        self.assertEqual(
            output.getvalue().strip(),
            "ID: 3, Name: Charlie, Skill: Python",
        )

    def test_manager_and_employee_have_different_extra_members(self):
        # 관리자와 직원을 각각 한 명씩 만듭니다.
        manager = Manager(2, "Bob", "Team Leader")
        employee = Employee(3, "Charlie", "Python")
        # 관리자는 skill을 가지고 있지 않은지 확인합니다.
        self.assertFalse(hasattr(manager, "skill"))
        # 직원은 title을 가지고 있지 않은지 확인합니다.
        self.assertFalse(hasattr(employee, "title"))


if __name__ == "__main__":
    # 이 파일을 직접 실행했을 때만 10개의 검사를 시작합니다.
    unittest.main()