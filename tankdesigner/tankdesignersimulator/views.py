from django.shortcuts import render, redirect
from django.contrib import messages


def design(request):

    if request.method == 'POST':

        # First part fields
        # --------------------------------------------------------------------------------------------

        tank_height = request.POST.get('tankHeight')
        tank_radius = request.POST.get('tankRadius')
        working_temperature = request.POST.get('workingTemperature')
        working_pressure = request.POST.get('workingPressure')
        cloak_pressure_design = request.POST.get('cloakPressureDesign')
        external_cloak_radius = request.POST.get('externalClockRadius')
        working_effort_admissible = request.POST.get('workingEffortAdmissibleAcerInoxTemp')
        efficiency_of_welded_join = request.POST.get('efficiencyOfTheWeldedJoin')
        domus_pressure_design = request.POST.get('domusPressureDesign')
        external_domus_radius = request.POST.get('externalDomusRadius')

        # Second part fields
        # --------------------------------------------------------------------------------------------

        t_environment = request.POST.get('tEnvironment')
        t_nitro = request.POST.get('tNitro')
        k1 = request.POST.get('K1')
        k2 = request.POST.get('K2')
        kisolation = request.POST.get('Kisolation')
        r1_int = request.POST.get('R1int')
        r1_ext = request.POST.get('R1ext')
        r2_int = request.POST.get('R2int')
        r2_ext = request.POST.get('R2ext')
        lc = request.POST.get('Lc')
        hamb = request.POST.get('hamb')

        # Aux variables
        # -------------------------------------------------------------------------------------------

        Pi = 3.1416


        # Data processing
        # -------------------------------------------------------------------------------------------

        print("Tank Height:", tank_height)
        print("Tank Radius:", tank_radius)
        print("Working Temperature:", working_temperature)
        print("Working Pressure:", working_pressure)
        print("Cloak Pressure Design:", cloak_pressure_design)
        print("External Cloak Radius:", external_cloak_radius)
        print("Working Effort Admissible:", working_effort_admissible)
        print("Efficiency of Welded Join:", efficiency_of_welded_join)
        print("Domus Pressure Design:", domus_pressure_design)
        print("External Domus Radius:", external_domus_radius)
        print("T Environment:", t_environment)
        print("T Nitro:", t_nitro)
        print("K1:", k1)
        print("K2:", k2)
        print("K Isolation:", kisolation)
        print("R1 Intern:", r1_int)
        print("R1 Extern:", r1_ext)
        print("R2 Intern:", r2_int)
        print("R2 Extern:", r2_ext)
        print("Lc:", lc)
        print("h amb:", hamb)

        # Calculations
        # -----------------------------------------------------

        pi = 3.1416
        v_cilinder = pi * pow(tank_radius, 2) * tank_height
        v_dome = (2 / 3) * pi * pow(tank_radius, 3)
        V = (v_cilinder + v_dome) * 1000  # L
        print('V', V)
        n = (working_pressure * V) / (0.0821 * T)
        print('n', n)
        nitrogen_moles_mass = 28  # g/mol
        m = n * nitrogen_moles_mass * 0.001  # Kg
        print('m', m)
        steal_thickness = 0.01  # m
        area_steel = 2 * pi * tank_radius * tank_height + 3 * pi * tank_radius * tank_radius
        print('Area Steel', area_steel)
        v_steel = area_steel * steal_thickness
        print('Volume Steel', v_steel)
        steel_density = 7850  # kg/m3
        isolate_material_density = 100  # kg/m3
        isolate_material_thickness = 0.05  # mm
        v_external_tank = pi * pow((tank_radius + isolate_material_thickness), 2) * tank_height + ( (2 / 3) * pi * pow(tank_radius + isolate_material_thickness, 3))
        print('Volume external Tank', v_external_tank)
        v_internal_tank = (pi * pow(tank_radius, 2) * tank_height) + ((2 / 3) * pi * pow(tank_radius, 3))
        print('V internal Tank', v_internal_tank)
        v_isolation = v_external_tank - v_internal_tank
        print('vIsolation', v_isolation)
        metalic_weight = Vsteel * steel_density  # kg
        print('metalic weight', metalic_weight)
        isolating_material_weight = v_isolation * isolate_material_density  # kg
        print('isolating material weight', isolating_material_weight)
        empty_tank_weight = isolating_material_weight + metalic_weight
        print('Empty Tank Weight', empty_tank_weight)
        full_tank_weight = empty_tank_weight + m
        print('Full Tank Weight', full_tank_weight)

        # Building material acerinox AISI 304
        # -----------------------------------
        # Internal Tank
        # ------------------------------
        # Cloak design / Diseño de manto
        # ------------------------------

        t_cloak = cloak_pressure_design * external_cloak_radius / ((working_effort_admissible * efficiency_of_welded_join) - 0.6 * cloak_pressure_design)

        print("Cloak", t_cloak, "inches")
        print("Cloak", t_cloak * 25.1, "inches")

        # Domus design / diseño del domo
        # ------------------------------

        t_domus = (domus_pressure_design * 2*external_domus_radius) / ((2 * working_effort_admissible * efficiency_of_welded_join) - (0.2 * domus_pressure_design))

        print("Domus", t_domus, "inches")
        print("Domus", t_domus * 25.1, "inches")

        # Thermal design / Diseño termico
        # ---------------------------------------

        Rtot = (math.log((r1_ext / r1_int)) / (2 * Pi * k1)) + (math.log((r2_int / r1_ext)) / (2 * Pi * kisolation)) + (
                    math.log((r2_ext / r2_int)) / (2 * Pi * k2)) + (1 / (2 * Pi * hamb * r2_ext))
        print('Rtot', Rtot)

        q = ((t_environment - t_nitro) / Rtot) * lc

        print('Heat Exchange (q)', q)


    return render(request, 'design.html')
