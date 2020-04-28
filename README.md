# Areal
Симуляция растений
Описание симуляции (если кому интересно).

#КЛЕТКИ ИГРОВОГО ПОЛЯ
Игровое поле разделено на клетки (что поначалу незаметно). Каждая клетка имеет запас питательных веществ (почвы). По мере того, как почва заканчивается, клетка темнеет. Это позволяет оценить, достаточно ли у растений питания. На каждой клетке может располагаться до 5 растений. А так же неограниченное количество семян и гнили. 

#РАСТЕНИЯ
Растения обозначены зелеными квадратиками. Они тянут из клеток почву, превращая ее в собственную массу. Когда растение достигает максимальной установленной массы, оно отбрасывает одно семечко, а до этого возможности размножаться у него нет. Если на клетке заканчивается почва, растение начинает голодать (его цвет становится темно-зеленым).  Его масса начинает уменьшаться. Дело в том, что у растения есть две массы. Реальная и мнимая. Реальная — это сколько растение весит в данный момент. Мнимая масса (я называю ее энергией) — это масса почвы, потребленная растением с за всю жизнь. Вся поглощаемая растением почва делится на две половины: 1) часть, которая переходит в реальную массу; 2) часть, которая служит для набора или поддержания текущего веса. Если на клетке закончилась почва, растение будет тратить энергию, необходимую на поддержание жизни, перерабатывая свою реальную массу. Если масса растения приближается к определенной небольшой величине, растение погибает и вся скрытая масса (энергия) переходит в гниль. По достижении предельного возраста растение также погибает.
В программе пока что нет генома. Все растения одинаковые. Поэтому симуляции протекают предсказуемо однообразно. Через графический интерфейс можно задать сид генератора случайных чисел, но по большому счету он влияет только на координаты растений. Более важные настройки можно покрутить через файл constants.py

#СЕМЕНА
Растение выбрасывает по одной семечке за раз. Семечка (обозначена золотистым квадратиком) может упасть на родную клетку, а может на одну из смежных. На прорастание семечки есть два условия: 1) количество почвы на клетке, при котором происходит прорастание. Это позволяет дождаться благоприятных условий, чтобы проросшее растение не умерло от голода. 2) Задержка прорастания. Например, прежде чем взойти, растение должно полгода пролежать в земле. Это довольно искусственное ограничение, но запрет на прорастание можно установить в нуль.
Далее, если условия на клетке благоприятные, семечку дается команда на прорастание. Если на клетке уже имеется пять растений, семечка погибает.
Если семечке не удалось прорасти в течение определенного периода, она превращается в гниль. Семечка не может ждать вечно.

#ГНИЛЬ 
Мертвые растения и семена превращаются в гниль.  Гниль тоже имеет массу. Она равна не  реальной массе растений (довольно скромной), а мнимой массе, «энергии», которую они накапливали всю жизнь. Гниль для растений несъедобна, но она понемногу перерабатывается в почву. Происходит это довольно медленно. Растения выедают почву с клеток гораздо быстрее, чем она успевает восстанавливаться за счет перегноя. Так что клетки периодически пустеют — ничего кроме гнили на них нет, растения здесь жить не могут.

#ЛОГИРОВАНИЕ
В процессе симуляции в папку с программой пишутся три csv файла. Так что при желании можно проследить за жизнью каждого растения.

ГОРЯЧИЕ КЛАВИШИ:
- эскейп: рестарт симуляции
- пробел: пуск/стоп
- вправо: шаг вперед.