-- Skript pro výpočet odometrie z RPM a PWM pro řízení smykem a EKF fúzi

-- 1. KONFIGURACE TVÉHO STROJE
local KOLO_POLOMER = 0.22
local PREVOD = 25.0       
local OBVOD_KOLA = 2.0 * math.pi * KOLO_POLOMER

local dist_L = 0.0
local dist_R = 0.0

-- Pomocná funkce pro bezpečný převod C++ objektů na čisté Lua číslo
local function get_num(val)
    if not val then return 0.0 end
    if type(val) == "userdata" and val.tofloat then 
        return val:tofloat() 
    end
    return tonumber(val) or 0.0
end

local last_update = get_num(millis())

-- 2. HLAVNÍ SMYČKA SKRIPTU
function update_odometry()
    local now = get_num(millis())
    local dt_ms = now - last_update -- Časový krok v milisekundách
    local dt = dt_ms / 1000.0       -- Časový krok v sekundách
    last_update = now

    -- Načtení aktuálních RPM a PWM
    local rpm_L = get_num(RPM:get_rpm(0))
    local rpm_R = get_num(RPM:get_rpm(1))
    local pwm_L = get_num(SRV_Channels:get_output_pwm(73))
    local pwm_R = get_num(SRV_Channels:get_output_pwm(74))

    if pwm_L == 0.0 then pwm_L = 1500 end
    if pwm_R == 0.0 then pwm_R = 1500 end

    -- Odhad směru
    local dir_L = 0
    local dir_R = 0
    if pwm_L > 1550 then dir_L = 1 elseif pwm_L < 1450 then dir_L = -1 end
    if pwm_R > 1550 then dir_R = 1 elseif pwm_R < 1450 then dir_R = -1 end

    -- Výpočet ujeté vzdálenosti za tento časový úsek (delta)
    local delta_dist_L = ((rpm_L / PREVOD) / 60.0) * OBVOD_KOLA * dt * dir_L
    local delta_dist_R = ((rpm_R / PREVOD) / 60.0) * OBVOD_KOLA * dt * dir_R

    -- Celková kumulovaná vzdálenost
    dist_L = dist_L + delta_dist_L
    dist_R = dist_R + delta_dist_R

    -- 1. Odeslání do telemetrie (Mission Planner / ODROID)
    gcs:send_named_float("Dist_L", dist_L)
    gcs:send_named_float("Dist_R", dist_R)

    -- 2. VSTŘÍKNUTÍ DAT DO NAVIGAČNÍHO FILTRU (EKF3)
    -- Zkontrolujeme, jestli ArduPilot už zinicializoval WENC modul
    if wheel_encoder then
        -- Používáme pcall (protected call), aby skript nespadl, pokud má tvoje verze ArduPilotu mírně jinou syntaxi.
        -- Funkce obvykle očekává: (instance, kumulovaná_vzdálenost, delta_čas_v_ms)
        pcall(function()
            local dt_ms_uint = math.floor(dt_ms)
            wheel_encoder:update(0, dist_L, dt_ms_uint)
            wheel_encoder:update(1, dist_R, dt_ms_uint)
        end)
    end

    return update_odometry, 20
end

return update_odometry, 1000