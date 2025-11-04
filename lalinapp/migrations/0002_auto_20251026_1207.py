from django.db import migrations

def seed_data(apps, schema_editor):
    Department = apps.get_model('lalinapp', 'Department')
    Position = apps.get_model('lalinapp', 'Position')

    # Tạo phòng ban và chức vụ
    departments = {
        'Phòng Thiết Kế': [
            'Nhân viên thiết kế',
            'Trưởng phòng thiết kế',
        ],
        'Phòng Sản Xuất': [

            'Nhân viên sản xuất',
            'Trưởng phòng sản xuất',

        ],
        'Phòng Kinh Doanh': [

            'Nhân viên kinh doanh',
            'Trưởng phòng kinh doanh',
       ],
        'Phòng Marketing': [

            'Nhân viên marketing',
            'Trưởng phòng marketing',
        ],
        'Phòng Nhân Sự': [

            'Nhân viên nhân sự',
            'Trưởng phòng nhân sự',
        ],
        'Phòng Tài Chính': [

            'Nhân viên tài chính',
            'Trưởng phòng tài chính',
        ],
        'Phòng IT': [

            'Nhân viên kỹ thuật',
            'Trưởng phòng IT',
        ],
    }

    # Gán lương cơ bản tạm thời cho mỗi phòng ban
    base_salaries = {
        'Phòng Thiết Kế': 8000000,
        'Phòng Sản Xuất': 6000000,
        'Phòng Kinh Doanh': 7000000,
        'Phòng Marketing': 7500000,
        'Phòng Nhân Sự': 9000000,
        'Phòng Tài Chính': 8500000,
        'Phòng IT': 9000000,
    }

    for dept_name, positions in departments.items():
        dept = Department.objects.create(name=dept_name, base_salary=base_salaries[dept_name])
        for i, pos_name in enumerate(positions):
            coef = 1.0 + i * 0.3  # hệ số lương tăng dần
            Position.objects.create(name=pos_name, department=dept, salary_coef=coef)

class Migration(migrations.Migration):

    dependencies = [
        ('lalinapp', '0001_initial'),  # sửa lại nếu cần
    ]

    operations = [
        migrations.RunPython(seed_data),
    ]
