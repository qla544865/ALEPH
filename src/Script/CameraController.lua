-- CameraController.lua
-- Controls camera panning, zooming, and resetting via Lua

local CameraController = {
    config = {
        speed = 300.0,                 -- Base camera pan speed (world units/sec)
        fast_speed_multiplier = 2.5,   -- Speed multiplier when holding Shift
        zoom_speed = 8.0,              -- Keyboard zoom speed
        wheel_zoom_speed = 40.0,       -- Mouse wheel zoom factor
        enable_keyboard = true,
        enable_mouse_drag = true,
        enable_zoom = true,
        enable_reset = true,
    },
    
    -- Internal drag state
    prev_mouse_pos = nil,
    drag_start_cam = nil,
}

function CameraController.init()
    print("[CameraController] Initialised!")
    print("[CameraController] Controls: WASD/Arrows to pan, Shift for fast pan, Mouse Right-Drag to pan, +/- or Mouse Wheel to zoom, R to reset")
end

function CameraController.update(dt)
    if dt == nil or dt <= 0 then
        return
    end

    local scale = Camera.get_scale()
    if scale <= 0 then
        scale = 1.0
    end

    -- -----------------------------------------------------------------
    -- 1. Keyboard Panning (WASD + Arrow Keys)
    -- -----------------------------------------------------------------
    if CameraController.config.enable_keyboard then
        local pan_speed = (CameraController.config.speed / scale) * dt

        -- Speed boost with Shift
        if Input.is_key_pressed("shift") or Input.is_key_pressed("lshift") or Input.is_key_pressed("rshift") then
            pan_speed = pan_speed * CameraController.config.fast_speed_multiplier
        end

        local dx = 0
        local dy = 0

        if Input.is_key_pressed("w") or Input.is_key_pressed("up") then
            dy = dy - pan_speed
        end
        if Input.is_key_pressed("s") or Input.is_key_pressed("down") then
            dy = dy + pan_speed
        end
        if Input.is_key_pressed("a") or Input.is_key_pressed("left") then
            dx = dx - pan_speed
        end
        if Input.is_key_pressed("d") or Input.is_key_pressed("right") then
            dx = dx + pan_speed
        end

        if dx ~= 0 or dy ~= 0 then
            Camera.move(dx, dy)
        end
    end

    -- -----------------------------------------------------------------
    -- 2. Mouse Drag Panning (Right Mouse Button)
    -- -----------------------------------------------------------------
    if CameraController.config.enable_mouse_drag then
        local is_right_down = Input.is_mouse_pressed(3) or Input.is_mouse_pressed("right")
        
        if is_right_down then
            local mx, my = Input.get_mouse_pos()
            
            if not CameraController.prev_mouse_pos then
                CameraController.prev_mouse_pos = { x = mx, y = my }
                local cx, cy = Camera.get_pos()
                CameraController.drag_start_cam = { x = cx, y = cy }
            else
                local delta_x = mx - CameraController.prev_mouse_pos.x
                local delta_y = my - CameraController.prev_mouse_pos.y

                Camera.set_pos(
                    CameraController.drag_start_cam.x - (delta_x / scale),
                    CameraController.drag_start_cam.y - (delta_y / scale)
                )
            end
        else
            CameraController.prev_mouse_pos = nil
            CameraController.drag_start_cam = nil
        end
    end

    -- -----------------------------------------------------------------
    -- 3. Zooming (+ / - keys and Mouse Wheel)
    -- -----------------------------------------------------------------
    if CameraController.config.enable_zoom then
        -- Keyboard zoom
        if Input.is_key_pressed("minus") or Input.is_key_pressed("-") then
            Camera.change_fov(-CameraController.config.zoom_speed * dt)
        end
        if Input.is_key_pressed("equals") or Input.is_key_pressed("=") or Input.is_key_pressed("+") then
            Camera.change_fov(CameraController.config.zoom_speed * dt)
        end

        -- Mouse wheel scroll zoom
        local scroll = Input.get_scroll()
        if scroll ~= 0 then
            Camera.change_fov(scroll * CameraController.config.wheel_zoom_speed * dt)
        end
    end

    -- -----------------------------------------------------------------
    -- 4. Quick Reset (R Key)
    -- -----------------------------------------------------------------
    if CameraController.config.enable_reset then
        if Input.is_key_pressed("r") then
            Camera.reset()
        end
    end
end

return CameraController
