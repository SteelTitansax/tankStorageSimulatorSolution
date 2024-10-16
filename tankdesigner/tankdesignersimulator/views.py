from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
import math
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

# Create your views here.
def home(request):

    return render(request,'home.html')

def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        try:
         if request.POST['password1'] == request.POST['password2']:
            user = User.objects.create_user(username=request.POST['username'],password = request.POST['password1'])
            user.save()
            login(request,user)
            return redirect('design')
        except IntegrityError:
            return render(request, 'signup.html', {
                'form': UserCreationForm,
                'error': 'User already exists'
            })

    return render(request, 'signup.html', {
        'form': UserCreationForm,
        'error': 'Password do not match'
    })

@login_required
def signout(request):
    logout(request)
    return redirect(home)

def signin(request):
    if request.method == 'GET':

        return render(request, 'signin.html',{
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password = request.POST['password']
        )
        if user is None :
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error' : 'Username or passowrd is incorrect'
            })
        else:
            login(request,user)
            return redirect('design')



@login_required
def design(request):
    if request.method == 'POST':
        # Primer conjunto de campos
        tank_height = float(request.POST.get('tankHeight'))
        tank_radius = float(request.POST.get('tankRadius'))
        working_temperature = float(request.POST.get('workingTemperature'))
        working_pressure = float(request.POST.get('workingPressure'))

        # Campos adicionales
        cloak_pressure_design = float(request.POST.get('cloakPressureDesign'))
        external_cloak_radius = float(request.POST.get('externalClockRadius'))
        working_effort_admissible = float(request.POST.get('workingEffortAdmissibleAcerInoxTemp'))
        efficiency_of_welded_join = float(request.POST.get('efficiencyOfTheWeldedJoin'))
        domus_pressure_design = float(request.POST.get('domusPressureDesign'))
        external_domus_radius = float(request.POST.get('externalDomusRadius'))

        # Campos de la segunda parte
        t_environment = float(request.POST.get('tEnvironment'))
        t_nitro = float(request.POST.get('tNitro'))
        k1 = float(request.POST.get('K1'))
        k2 = float(request.POST.get('K2'))
        kisolation = float(request.POST.get('Kisolation'))
        r1_int = float(request.POST.get('R1int'))
        r1_ext = float(request.POST.get('R1ext'))
        r2_int = float(request.POST.get('R2int'))
        r2_ext = float(request.POST.get('R2ext'))
        lc = float(request.POST.get('Lc'))
        hamb = 5

        # Realiza los cálculos (puedes extraer esta lógica a una función separada)
        results = perform_calculations(
            tank_height, tank_radius, working_temperature, working_pressure,
            cloak_pressure_design, external_cloak_radius, working_effort_admissible,
            efficiency_of_welded_join, domus_pressure_design, external_domus_radius,
            t_environment, t_nitro, k1, k2, kisolation, r1_int, r1_ext, r2_int, r2_ext, lc, hamb
        )

        request.session['results'] = results
        return redirect('recalculate')

    return render(request, 'design.html')


def perform_calculations(tank_height, tank_radius, working_temperature, working_pressure,
                         cloak_pressure_design, external_cloak_radius, working_effort_admissible,
                         efficiency_of_welded_join, domus_pressure_design, external_domus_radius,
                         t_environment, t_nitro, k1, k2, kisolation, r1_int, r1_ext, r2_int, r2_ext, lc, hamb):
    # Lógica de cálculos
    Pi = 3.1416
    v_cilinder = Pi * pow(tank_radius, 2) * tank_height
    v_dome = (2 / 3) * Pi * pow(tank_radius, 3)
    V = round((v_cilinder + v_dome) * 1000, 2)  # L
    n = round((working_pressure * V) / (0.0821 * working_temperature), 2)
    nitrogen_moles_mass = 28  # g/mol
    m = round(n * nitrogen_moles_mass * 0.001, 2)  # Kg

    # Continúa con el resto de los cálculos...

    # Por ejemplo, el peso metálico y otros cálculos
    steel_thickness = 0.01  # m
    area_steel = round(2 * Pi * tank_radius * tank_height + 3 * Pi * tank_radius * tank_radius, 2)
    v_steel = round(area_steel * steel_thickness, 2)
    steel_density = 7850  # kg/m3
    isolate_material_density = 100  # kg/m3
    isolate_material_thickness = 0.05  # mm
    v_external_tank = round(Pi * pow((tank_radius + isolate_material_thickness), 2) * tank_height + (
            (2 / 3) * Pi * pow(tank_radius + isolate_material_thickness, 3)), 2)
    v_internal_tank = round((Pi * pow(tank_radius, 2) * tank_height) + ((2 / 3) * Pi * pow(tank_radius, 3)), 2)
    v_isolation = round(v_external_tank - v_internal_tank, 2)
    metallic_weight = round(v_steel * steel_density, 2)  # kg
    isolating_material_weight = round(v_isolation * isolate_material_density, 2)  # kg
    empty_tank_weight = round(isolating_material_weight + metallic_weight, 2)
    full_tank_weight = round(empty_tank_weight + m, 2)

    # Calcular grosor del manto y domo
    t_cloak = round(cloak_pressure_design * external_cloak_radius / (
            (working_effort_admissible * efficiency_of_welded_join) - 0.6 * cloak_pressure_design), 2)
    t_domus = round((domus_pressure_design * 2 * external_domus_radius) / (
            (2 * working_effort_admissible * efficiency_of_welded_join) - (0.2 * domus_pressure_design)), 2)

    # Cálculo térmico
    Rtot = round(
        (math.log((r1_ext / r1_int)) / (2 * Pi * k1)) + (math.log((r2_int / r1_ext)) / (2 * Pi * kisolation)) +
        (math.log((r2_ext / r2_int)) / (2 * Pi * k2)) + (1 / (2 * Pi * hamb * r2_ext)), 2)

    q = round(((t_environment - t_nitro) / Rtot) * lc, 2)

    # Guardar resultados
    results = {
        'v': V,
        'n': n,
        'm': m,
        'metallic_weight': metallic_weight,
        'isolating_material_weight': isolating_material_weight,
        'empty_tank_weight': empty_tank_weight,
        'full_tank_weight': full_tank_weight,
        't_cloak_inches': t_cloak,
        't_cloak_mm': round(t_cloak * 25.4, 2),
        't_domus_inches': t_domus,
        't_domus_mm': round(t_domus * 25.4, 2),
        'q': q,
        'tank_height': tank_height,
        'tank_radius': tank_radius,
        'working_temperature': working_temperature,
        'working_pressure': working_pressure,
        'cloak_pressure_design': cloak_pressure_design,
        'external_cloak_radius': external_cloak_radius,
        'working_effort_admissible': working_effort_admissible,
        'efficiency_of_welded_join': efficiency_of_welded_join,
        'domus_pressure_design': domus_pressure_design,
        'external_domus_radius': external_domus_radius,
        't_environment': t_environment,
        't_nitro': t_nitro,
        'k1': k1,
        'k2': k2,
        'kisolation': kisolation,
        'r1_int': r1_int,
        'r1_ext': r1_ext,
        'r2_int': r2_int,
        'r2_ext': r2_ext,
        'lc': lc,
        'hamb': hamb,
    }

    return results

@login_required
def recalculate(request):
        if request.method == 'POST':
            # Get form values
            tank_height = float(request.POST.get('tankHeight'))
            tank_radius = float(request.POST.get('tankRadius'))
            working_temperature = float(request.POST.get('workingTemperature'))
            working_pressure = float(request.POST.get('workingPressure'))

            # Get result parameters from the form
            results = request.session.get('results', {})

            # Split in variables
            cloak_pressure_design = results.get('cloak_pressure_design')
            external_cloak_radius = results.get('external_cloak_radius')
            working_effort_admissible = results.get('working_effort_admissible')
            efficiency_of_welded_join = results.get('efficiency_of_welded_join')
            domus_pressure_design = results.get('domus_pressure_design')
            external_domus_radius = results.get('external_domus_radius')
            t_environment = results.get('t_environment')
            t_nitro = results.get('t_nitro')
            k1 = results.get('k1')
            k2 = results.get('k2')
            kisolation = results.get('kisolation')
            r1_int = results.get('r1_int')
            r1_ext = results.get('r1_ext')
            r2_int = results.get('r2_int')
            r2_ext = results.get('r2_ext')
            lc = results.get('lc')
            hamb = results.get('hamb')

            # Recalculate with new parameters
            new_results = perform_calculations(
                tank_height, tank_radius, working_temperature, working_pressure,
                cloak_pressure_design, external_cloak_radius, working_effort_admissible,
                efficiency_of_welded_join, domus_pressure_design, external_domus_radius,
                t_environment, t_nitro, k1, k2, kisolation, r1_int, r1_ext, r2_int, r2_ext, lc, hamb
            )

            # Update sesion results
            request.session['results'] = new_results

            return render(request, 'recalculate.html', {'results': new_results})

        # If is GET request just show the results
        results = request.session.get('results', {})
        return render(request, 'recalculate.html', {'results': results})

@login_required
def report(request):
    results = request.session.get('results', {})
    return render(request, 'report.html', {'results': results})


@csrf_exempt
def create_report(request):
    if request.method == 'POST':
        # Extraer resultados de la sesión
        results = request.session.get('results', {})

        # Crear el payload JSON con los resultados
        payload = {
            'tank_height': results.get('tank_height'),
            'tank_radius': results.get('tank_radius'),
            'working_temperature': results.get('working_temperature'),
            'working_pressure': results.get('working_pressure'),
            'cloak_pressure_design': results.get('cloak_pressure_design'),
            'external_cloak_radius': results.get('external_cloak_radius'),
            'working_effort_admissible': results.get('working_effort_admissible'),
            'efficiency_of_welded_join': results.get('efficiency_of_welded_join'),
            'domus_pressure_design': results.get('domus_pressure_design'),
            'external_domus_radius': results.get('external_domus_radius'),
            't_environment': results.get('t_environment'),
            't_nitro': results.get('t_nitro'),
            'k1': results.get('k1'),
            'k2': results.get('k2'),
            'kisolation': results.get('kisolation'),
            'r1_int': results.get('r1_int'),
            'r1_ext': results.get('r1_ext'),
            'r2_int': results.get('r2_int'),
            'r2_ext': results.get('r2_ext'),
            'lc': results.get('lc'),
            'hamb': results.get('hamb'),
            'v': results.get('v'),
            'n': results.get('n'),
            'm': results.get('m'),
            'metallic_weight': results.get('metallic_weight'),
            'isolating_material_weight': results.get('isolating_material_weight'),
            'empty_tank_weight': results.get('empty_tank_weight'),
            'full_tank_weight': results.get('full_tank_weight'),
            't_cloak_inches': results.get('t_cloak_inches'),
            't_cloak_mm': results.get('t_cloak_mm'),
            't_domus_inches': results.get('t_domus_inches'),
            't_domus_mm': results.get('t_domus_mm'),
            'q': results.get('q'),
        }

        print("Payload to Power Automate:", payload)  # Depuración

        # Lógica para enviar la solicitud HTTP a Power Automate
        response = requests.post(
            "https://prod-07.northcentralus.logic.azure.com:443/workflows/f56b9e1d913a41e3a66d6752e1fab99c/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=N2xX4ncMtUrKkcdUm-3iH4U3BTJg9HyoKTwlxSN5gSY",
            json=payload  # Enviar el payload JSON
        )

        if response.status_code == 200:
            return JsonResponse({'message': 'Report created successfully'}, status=200)
        elif response.status_code == 400:
            print("Response Content:", response.content)  # Imprimir el contenido de la respuesta
            return JsonResponse({'message': 'Failed to create report'}, status=400)


@csrf_exempt
def approval(request):
    if request.method == 'POST':
        # Extraer resultados de la sesión
        results = request.session.get('results', {})

        # Crear el payload JSON con los resultados
        payload = {
            'tank_height': results.get('tank_height'),
            'tank_radius': results.get('tank_radius'),
            'working_temperature': results.get('working_temperature'),
            'working_pressure': results.get('working_pressure'),
            'cloak_pressure_design': results.get('cloak_pressure_design'),
            'external_cloak_radius': results.get('external_cloak_radius'),
            'working_effort_admissible': results.get('working_effort_admissible'),
            'efficiency_of_welded_join': results.get('efficiency_of_welded_join'),
            'domus_pressure_design': results.get('domus_pressure_design'),
            'external_domus_radius': results.get('external_domus_radius'),
            't_environment': results.get('t_environment'),
            't_nitro': results.get('t_nitro'),
            'k1': results.get('k1'),
            'k2': results.get('k2'),
            'kisolation': results.get('kisolation'),
            'r1_int': results.get('r1_int'),
            'r1_ext': results.get('r1_ext'),
            'r2_int': results.get('r2_int'),
            'r2_ext': results.get('r2_ext'),
            'lc': results.get('lc'),
            'hamb': results.get('hamb'),
            'v': results.get('v'),
            'n': results.get('n'),
            'm': results.get('m'),
            'metallic_weight': results.get('metallic_weight'),
            'isolating_material_weight': results.get('isolating_material_weight'),
            'empty_tank_weight': results.get('empty_tank_weight'),
            'full_tank_weight': results.get('full_tank_weight'),
            't_cloak_inches': results.get('t_cloak_inches'),
            't_cloak_mm': results.get('t_cloak_mm'),
            't_domus_inches': results.get('t_domus_inches'),
            't_domus_mm': results.get('t_domus_mm'),
            'q': results.get('q'),
        }

        # Lógica para enviar la solicitud HTTP a Power Automate
        response = requests.post(
            "https://prod-07.northcentralus.logic.azure.com:443/workflows/f56b9e1d913a41e3a66d6752e1fab99c/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=N2xX4ncMtUrKkcdUm-3iH4U3BTJg9HyoKTwlxSN5gSY",
            json=payload  # Enviar el payload JSON
        )

        if response.status_code == 200:
            return JsonResponse({'message': 'Approval start completed'}, status=200)
        else:
            return JsonResponse({'message': 'Failed to initiate approval'}, status=400)
