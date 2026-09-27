


# abstraction (abc module + abstract methods)
from abc import ABC, abstractmethod


def format_currency(value):
   return "{:,.2f}".format(value)


# custom exception - Duplicate, negative, impossible, missing-data, and reprocessing errors
class PayrollException(Exception):
   pass


# Abstract base class
class Employee(ABC):
   TYPE_LABEL = "Employee"


   def __init__(self, employee_id, name, rate):
       if not employee_id or not name:
           raise PayrollException("Employee ID and name cannot be empty.")
       if rate < 0:
           raise PayrollException("Rate cannot be negative.")


       # encapsulation
       self.__employee_id = employee_id
       self.__name = name
       self.__rate = rate


   #controlled access to private attributes
   def get_employee_id(self):
       return self.__employee_id


   def get_name(self):
       return self.__name


   def get_rate(self):
       return self.__rate


   def set_rate(self, new_rate):
       if new_rate < 0:
           raise PayrollException("Rate cannot be negative.")
       self.__rate = new_rate


   # polymorphism
   def get_type_label(self):
       return self.TYPE_LABEL


   # abstract methods
   @abstractmethod
   def calculate_gross_pay(self, attendance):
       pass


   @abstractmethod
   def get_benefits(self, attendance):
       pass


   # magic methods
   def __str__(self):
       return "[{}] {} ({})".format(
           self.__employee_id, self.__name, self.get_type_label()
       )


   def __eq__(self, other):
       if not isinstance(other, Employee):
           return False
       return self.__employee_id == other.get_employee_id()




# EMPLOYEE SUBCLASSES


# inheritance - subclass 1
class RegularEmployee(Employee):


# Salary, overtime, and regular-benefit rules
   TYPE_LABEL = "Regular Employee"
   OVERTIME_MULTIPLIER = 1.25
   STANDARD_HOURS = 160
   STANDARD_DAYS = 22
   MONTHLY_BENEFIT = 2000


   def __init__(self, employee_id, name, monthly_salary):
       super().__init__(employee_id, name, monthly_salary)


   def calculate_gross_pay(self, attendance):
       monthly_salary = self.get_rate()
       hourly_equivalent = monthly_salary / self.STANDARD_HOURS
       daily_rate = monthly_salary / self.STANDARD_DAYS


       overtime_pay = attendance.get_overtime() * hourly_equivalent * self.OVERTIME_MULTIPLIER
       absence_deduction = attendance.get_absences() * daily_rate


       gross_pay = monthly_salary + overtime_pay - absence_deduction
       return max(gross_pay, 0)


   def get_benefits(self, attendance):
       return self.MONTHLY_BENEFIT


   def __str__(self):
       return super().__str__() + " - Rate: {}".format(format_currency(self.get_rate()))




# inheritance - subclass 2
class PartTimeEmployee(Employee):


 # Hourly compensation and limited-benefit rules
   TYPE_LABEL = "Part-Time Employee"
   OVERTIME_MULTIPLIER = 1.25
   BENEFIT_HOURS_THRESHOLD = 80
   LIMITED_BENEFIT = 300


   def __init__(self, employee_id, name, hourly_rate):
       super().__init__(employee_id, name, hourly_rate)


   def calculate_gross_pay(self, attendance):
       hourly_rate = self.get_rate()
       regular_pay = attendance.get_hours_worked() * hourly_rate
       overtime_pay = attendance.get_overtime() * hourly_rate * self.OVERTIME_MULTIPLIER
       gross_pay = regular_pay + overtime_pay
       return max(gross_pay, 0)


   def get_benefits(self, attendance):
       if attendance.get_hours_worked() >= self.BENEFIT_HOURS_THRESHOLD:
           return self.LIMITED_BENEFIT
       return 0


   def __str__(self):
       return super().__str__() + " - Rate: {}".format(format_currency(self.get_rate()))




# inheritance - subclass 3
class CommissionEmployee(Employee):


   #Base amount and sales-commission rules
   TYPE_LABEL = "Commission Employee"
   COMMISSION_RATE = 0.05
   HIGH_SALES_THRESHOLD = 20000
   HIGH_SALES_BONUS = 500
   STANDARD_BONUS = 100


   def __init__(self, employee_id, name, base_amount):
       super().__init__(employee_id, name, base_amount)


   def calculate_gross_pay(self, attendance):
       base_amount = self.get_rate()
       commission = attendance.get_sales() * self.COMMISSION_RATE
       gross_pay = base_amount + commission
       return max(gross_pay, 0)


   def get_benefits(self, attendance):
       if attendance.get_sales() >= self.HIGH_SALES_THRESHOLD:
           return self.HIGH_SALES_BONUS
       return self.STANDARD_BONUS


   def __str__(self):
       return super().__str__() + " - Rate: {}".format(format_currency(self.get_rate()))




# ATTENDANCE RECORD


class AttendanceRecord:


   MAX_HOURS = 744
   MAX_ABSENCES = 31


   def __init__(self, employee, hours_worked, overtime, absences, sales=0):
       if hours_worked < 0:
           raise PayrollException("Hours worked cannot be negative.")
       if overtime < 0:
           raise PayrollException("Overtime hours cannot be negative.")
       if absences < 0:
           raise PayrollException("Absences cannot be negative.")
       if sales < 0:
           raise PayrollException("Sales cannot be negative.")
       if hours_worked > self.MAX_HOURS:
           raise PayrollException("Impossible number of hours worked.")
       if absences > self.MAX_ABSENCES:
           raise PayrollException("Impossible number of absences.")


       self.employee = employee
       self.hours_worked = hours_worked
       self.overtime = overtime
       self.absences = absences
       self.sales = sales
       self.processed = False


   def get_hours_worked(self):
       return self.hours_worked


   def get_overtime(self):
       return self.overtime


   def get_absences(self):
       return self.absences


   def get_sales(self):
       return self.sales


   def is_processed(self):
       return self.processed


   def mark_processed(self):
       self.processed = True


   # magic method
   def __str__(self):
       return ("Attendance[{}] Hours: {}, OT: {}, Absences: {}, Sales: {}"
               .format(self.employee.get_employee_id(), self.hours_worked,
                       self.overtime, self.absences, format_currency(self.sales)))






# PAYROLL ENTRY
class PayrollEntry:


   TAX_RATE = 0.10


   def __init__(self, employee, attendance):
       self.employee = employee
       self.attendance = attendance
       self.gross_pay = 0
       self.deductions = 0
       self.benefits = 0
       self.net_pay = 0
       self.status = "Pending"


   def process(self):
       if self.status == "Processed":
           raise PayrollException("This payroll entry has already been processed.")


       gross = self.employee.calculate_gross_pay(self.attendance)
       deductions = round(gross * self.TAX_RATE, 2)
       benefits = self.employee.get_benefits(self.attendance)
       net = gross - deductions + benefits


       # freeze computed values
       self.gross_pay = round(gross, 2)
       self.deductions = deductions
       self.benefits = round(benefits, 2)
       self.net_pay = round(net, 2)
       self.status = "Processed"


   # magic methods
   def __str__(self):
       return ("Payslip for {}\n"
               "  Gross Pay:  {}\n"
               "  Deductions: {}\n"
               "  Benefits:   {}\n"
               "  Net Pay:    {}\n"
               "  Status:     {}"
               .format(self.employee, format_currency(self.gross_pay),
                       format_currency(self.deductions), format_currency(self.benefits),
                       format_currency(self.net_pay), self.status))


   def __eq__(self, other):
       if not isinstance(other, PayrollEntry):
           return False
       return (self.employee == other.employee and
               self.attendance is other.attendance)




# PAYROLL MANAGER


class PayrollManager:


   def __init__(self):
       self.employees = {}
       self.attendance_records = []
       self.payroll_history = []


   def register_employee(self, employee):
       if employee.get_employee_id() in self.employees:
           raise PayrollException(
               "Duplicate employee ID: {}".format(employee.get_employee_id()))
       self.employees[employee.get_employee_id()] = employee


   def record_work_data(self, employee_id, hours_worked, overtime, absences, sales=0):
       if employee_id not in self.employees:
           raise PayrollException("Employee ID not found: {}".format(employee_id))


       employee = self.employees[employee_id]
       record = AttendanceRecord(employee, hours_worked, overtime, absences, sales)
       self.attendance_records.append(record)
       return record


   def _get_latest_attendance(self, employee_id):
       for record in reversed(self.attendance_records):
           if record.employee.get_employee_id() == employee_id:
               return record
       return None


   def process_employee_payroll(self, employee_id):
       if employee_id not in self.employees:
           raise PayrollException("Employee ID not found: {}".format(employee_id))


       employee = self.employees[employee_id]
       record = self._get_latest_attendance(employee_id)


       if record is None:
           raise PayrollException(
               "Cannot process payroll. Work data is missing for {}.".format(employee_id))


       if record.is_processed():
           raise PayrollException(
               "Payroll for employee {} has already been processed.".format(employee_id))


       entry = PayrollEntry(employee, record)
       entry.process()
       record.mark_processed()
       self.payroll_history.append(entry)
       return entry


   def process_all_payroll(self):
       results = []
       for employee_id in self.employees:
           try:
               self.process_employee_payroll(employee_id)
               results.append((employee_id, "Payroll processed successfully"))
           except PayrollException as e:
               message = str(e)
               if "already been processed" in message:
                   results.append((employee_id, "Already processed"))
               elif "Work data is missing" in message:
                   results.append((employee_id, "Work data missing"))
               else:
                   results.append((employee_id, message))
       return results


   def get_latest_processed_entry(self, employee_id):
       for entry in reversed(self.payroll_history):
           if entry.employee.get_employee_id() == employee_id:
               return entry
       return None


   # magic method
   def __len__(self):
       return len(self.payroll_history)


 # REPORTS
   def report_cost_by_employee_type(self):


       # report 1
       print("PAYROLL COST BY EMPLOYEE TYPE")
       print()
       totals = {}
       for entry in self.payroll_history:
           label = entry.employee.get_type_label()
           totals[label] = totals.get(label, 0) + entry.net_pay


       if not totals:
           print("No processed payroll data yet.")
           return


       for label, total in totals.items():
           print("{}: {}".format(label, format_currency(total)))


   # report 2
   def report_highest_lowest_net_pay(self):
       print("HIGHEST AND LOWEST NET PAY")
       print()
       if not self.payroll_history:
           print("No processed payroll data yet.")
           return


       sorted_entries = sorted(self.payroll_history, key=lambda e: e.net_pay)
       lowest = sorted_entries[0]
       highest = sorted_entries[-1]


       print("Highest Net Pay:")
       print("{} - {} - {}".format(highest.employee.get_employee_id(),
                                    highest.employee.get_name(),
                                    format_currency(highest.net_pay)))
       print()
       print("Lowest Net Pay:")
       print("{} - {} - {}".format(lowest.employee.get_employee_id(),
                                    lowest.employee.get_name(),
                                    format_currency(lowest.net_pay)))


   # report 3
   def report_total_deductions_and_benefits(self):
       print("TOTAL DEDUCTIONS AND BENEFITS")
       print()
       if not self.payroll_history:
           print("No processed payroll data yet.")
           return




       total_deductions = sum(entry.deductions for entry in self.payroll_history)
       total_benefits = sum(entry.benefits for entry in self.payroll_history)


       print("Total Deductions: {}".format(format_currency(total_deductions)))
       print("Total Benefits:   {}".format(format_currency(total_benefits)))


   # report 4
   def report_overtime_or_zero_hours(self):
       print("EMPLOYEES WITH OVERTIME")
       print()
       overtime_records = list(filter(lambda r: r.get_overtime() > 0, self.attendance_records))
       if not overtime_records:
           print("No employees with overtime.")
       else:
           for record in overtime_records:
               print("{} - {} - {} hours".format(
                   record.employee.get_employee_id(),
                   record.employee.get_name(),
                   record.get_overtime()))


       print()
       print("EMPLOYEES WITH ZERO PAYABLE HOURS")
       print()
       zero_hour_records = list(filter(lambda r: r.get_hours_worked() == 0, self.attendance_records))
       if not zero_hour_records:
           print("No employees with zero payable hours.")
       else:
           for record in zero_hour_records:
               print("{} - {}".format(record.employee.get_employee_id(),
                                       record.employee.get_name()))


   def generate_reports(self):
       self.report_cost_by_employee_type()
       print()
       self.report_highest_lowest_net_pay()
       print()
       self.report_total_deductions_and_benefits()
       print()
       self.report_overtime_or_zero_hours()






# prepared data
def load_demo_data(manager):


   #  Regular Employees
   manager.register_employee(RegularEmployee("R001", "Trisha Mae Mabini", 25000))
   manager.register_employee(RegularEmployee("R002", "Acts James Jumaquio", 22000))
   manager.register_employee(RegularEmployee("R003", "Sam Paraiso", 30000))


   # Part-Time Employees
   manager.register_employee(PartTimeEmployee("P001", "Bia Ramirez", 150))
   manager.register_employee(PartTimeEmployee("P002", "Mich Gealon", 120))
   manager.register_employee(PartTimeEmployee("P003", "Mae Manocay", 100))


   # Commission Employees
   manager.register_employee(CommissionEmployee("C001", "Nicole Mendoza", 8000))
   manager.register_employee(CommissionEmployee("C002", "James Dela Cruz", 7000))
   manager.register_employee(CommissionEmployee("C003", "Mae Babon", 6000))
   manager.register_employee(CommissionEmployee("C004", "Bianca Cruz", 5000))




   manager.record_work_data("R001", hours_worked=160, overtime=5, absences=0)
   manager.record_work_data("R002", hours_worked=150, overtime=0, absences=2)
   manager.record_work_data("R003", hours_worked=160, overtime=10, absences=0)


   manager.record_work_data("P001", hours_worked=90, overtime=4, absences=0)
   manager.record_work_data("P002", hours_worked=60, overtime=0, absences=0)
   manager.record_work_data("P003", hours_worked=0, overtime=0, absences=0)


   manager.record_work_data("C001", hours_worked=160, overtime=0, absences=0, sales=25000)
   manager.record_work_data("C002", hours_worked=160, overtime=0, absences=0, sales=15000)
   manager.record_work_data("C003", hours_worked=160, overtime=0, absences=0, sales=5000)
   manager.record_work_data("C004", hours_worked=160, overtime=2, absences=1, sales=1000)




# MENU


def print_menu():
   print("=" * 40)
   print(" PAYROLL AND COMPENSATION SYSTEM")
   print("=" * 40)
   print()
   print("1. Register employee")
   print("2. Record work data")
   print("3. Process employee payroll")
   print("4. Process all payroll")
   print("5. Search employee")
   print("6. Display payslip")
   print("7. Show payroll history")
   print("8. Generate reports")
   print("9. Exit")
   print()




def read_number(prompt, number_type=float):
   raw = input(prompt).strip()
   try:
       return number_type(raw)
   except ValueError:
       raise PayrollException("Invalid numeric input.")




def print_payroll_block(title, employee, entry, name_label="Employee Name"):
   print()
   print("=" * 40)
   print(title.center(40))
   print("=" * 40)
   print("Employee ID: {}".format(employee.get_employee_id()))
   print("{}: {}".format(name_label, employee.get_name()))
   print("Employee Type: {}".format(employee.get_type_label()))
   print()
   print("Gross Pay:  {}".format(format_currency(entry.gross_pay)))
   print("Deductions: {}".format(format_currency(entry.deductions)))
   print("Benefits:   {}".format(format_currency(entry.benefits)))
   print("-" * 40)
   print("Net Pay:    {}".format(format_currency(entry.net_pay)))
   print()
   print("Status: {}".format(entry.status))
   print("=" * 40)


def register_employee_menu(manager):
   print("Select employee type:")
   print("1. Regular Employee")
   print("2. Part-Time Employee")
   print("3. Commission Employee")
   print()


   try:
       choice = input("Enter choice: ").strip()
       employee_id = input("Enter employee ID: ").strip()


       if employee_id in manager.employees:
           raise PayrollException("Duplicate employee ID: {}".format(employee_id))


       name = input("Enter employee name: ").strip()
       rate = read_number("Enter rate: ")


       if choice == "1":
           employee = RegularEmployee(employee_id, name, rate)
       elif choice == "2":
           employee = PartTimeEmployee(employee_id, name, rate)
       elif choice == "3":
           employee = CommissionEmployee(employee_id, name, rate)
       else:
           raise PayrollException("Invalid employee type choice.")


       manager.register_employee(employee)


   except PayrollException as e:
       print("\nError: {}".format(e))
   else:
       print("\nEmployee registered successfully.")
   finally:
       pass




def record_work_data_menu(manager):
   try:
       employee_id = input("Enter employee ID: ").strip()
       if employee_id not in manager.employees:
           raise PayrollException("Employee ID not found: {}".format(employee_id))


       employee = manager.employees[employee_id]


       hours_worked = read_number("Enter hours worked: ")
       if hours_worked < 0:
           raise PayrollException("Hours worked cannot be negative.")


       overtime = read_number("Enter overtime hours: ")
       if overtime < 0:
           raise PayrollException("Overtime hours cannot be negative.")


       absences = read_number("Enter absences: ", int)
       if absences < 0:
           raise PayrollException("Absences cannot be negative.")


       sales = 0
       if isinstance(employee, CommissionEmployee):
           sales = read_number("Enter sales: ")
           if sales < 0:
               raise PayrollException("Sales cannot be negative.")


       manager.record_work_data(employee_id, hours_worked, overtime, absences, sales)
       print("\nWork data recorded successfully.")


   except PayrollException as e:
       print("\nError: {}".format(e))




def process_employee_payroll_menu(manager):
   try:
       employee_id = input("Enter employee ID: ").strip()
       entry = manager.process_employee_payroll(employee_id)
       print_payroll_block("PAYROLL PROCESSED", entry.employee, entry)
   except PayrollException as e:
       print("\nError: {}".format(e))




def process_all_payroll_menu(manager):
   print("\nProcessing all eligible employees...\n")
   results = manager.process_all_payroll()
   for employee_id, status in results:
       print("{} - {}".format(employee_id, status))
   print("\nPayroll processing completed.")




def search_employee_menu(manager):
   employee_id = input("Enter employee ID: ").strip()
   if employee_id in manager.employees:
       employee = manager.employees[employee_id]
       print("\nEmployee Found\n")
       print("Employee ID: {}".format(employee.get_employee_id()))
       print("Name: {}".format(employee.get_name()))
       print("Type: {}".format(employee.get_type_label()))
       print("Rate: {:.2f}".format(employee.get_rate()))
   else:
       print("\nError: Employee not found.")




def display_payslip_menu(manager):
   employee_id = input("Enter employee ID: ").strip()
   entry = manager.get_latest_processed_entry(employee_id)
   if entry is None:
       print("\nError: Payroll record not found.")
       return
   print_payroll_block("PAYSLIP", entry.employee, entry, name_label="Name")




def display_payroll_history(manager):
   print()
   print("=" * 40)
   print("PAYROLL HISTORY".center(40))
   print("=" * 40)
   print()


   if len(manager) == 0:
       print("No payroll transactions yet.")
   else:
       for i, entry in enumerate(manager.payroll_history, start=1):
           print("{}. {} - {}".format(i, entry.employee.get_employee_id(), entry.employee.get_name()))
           print("   Type: {}".format(entry.employee.get_type_label()))
           print("   Net Pay: {}".format(format_currency(entry.net_pay)))
           print("   Status: {}".format(entry.status))
           print()


   print("=" * 40)




def main():
   manager = PayrollManager()
   load_demo_data(manager)


   # menu loop
   while True:
       print()
       print_menu()
       choice = input("Enter your choice: ").strip()
       print()


       try:
           if choice == "1":
               register_employee_menu(manager)
           elif choice == "2":
               record_work_data_menu(manager)
           elif choice == "3":
               process_employee_payroll_menu(manager)
           elif choice == "4":
               process_all_payroll_menu(manager)
           elif choice == "5":
               search_employee_menu(manager)
           elif choice == "6":
               display_payslip_menu(manager)
           elif choice == "7":
               display_payroll_history(manager)
           elif choice == "8":
               manager.generate_reports()
           elif choice == "9":
               print("Thank you for using the Payroll and Compensation System.")
               print("Goodbye!")
               break
           else:
               print("Invalid choice. Please select a number from 1 to 9.")
       except Exception as e:
           print("An unexpected error occurred: {}".format(e))




if __name__ == "__main__":
   main()
