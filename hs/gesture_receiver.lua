local port = 7777
local sock = hs.socket.udp.server(port)

if not sock then 
    hs.alert.show("Failed to start UDP server on port" .. port)
    return 
end

sock:receive(function(data, addr))
    if not data then return
    end

    local cmd, val = string.match(data, "^(%S+)%s+(-?%d+)") --TODO: understand regex why?
    if cmd == "SCROLL" and val then
        local dy = tonumber(val)
        -- Scroll wheel event: {dx,dy} in "scroll units"
        hs.eventtap.scrollWheel({0,dy}, {}, "pixel")
    end
end

hs.alert.show("Gesture receiver running on UDP " .. port)