local port = 7777

-- If reloading, close any previous server to avoid port weirdness
if _G.gestureSock then
  _G.gestureSock:close()
  _G.gestureSock = nil
end

hs.alert.show("gesture_receiver loaded on UDP " .. port)

-- Keep a GLOBAL reference so it won't be garbage collected
_G.gestureSock = hs.socket.udp.server(port)

if not _G.gestureSock then
  hs.alert.show("FAILED to bind UDP " .. port)
  return
end

_G.gestureSock:receive(function(data, addr)
  -- Protect callback: an error here can break the receive loop
  local ok, err = pcall(function()
    if not data then return end

    local cmd, val = string.match(data, "^(%S+)%s+(-?%d+)")
    if cmd == "SCROLL" and val then
      local dy = tonumber(val)
      -- For continuous scrolling, pixel feels best
      hs.eventtap.scrollWheel({0, dy}, {}, "pixel")
    end
  end)

  if not ok then
    print("gesture_receiver callback error:", err)
    hs.alert.show("gesture_receiver error (see console)")
  end
end)