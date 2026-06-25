---------------------------------------------------------------------------------- 
-- MAV Sense telemetry over UART
-- 
-- Author: Martin Falticko, MAV Sense s.r.o.
-- ________________________________________
--
-- Copyright [2024] MAV Sense s.r.o.
-- All Rights Reserved.
--
-- Redistribution and use in source and binary forms, with or without
-- modification, are permitted provided that the following conditions are met:
-- 
-- 1. Redistributions of source code must retain the above copyright notice, this
--    list of conditions and the following disclaimer.
-- 2. Redistributions in binary form must reproduce the above copyright notice,
--    this list of conditions and the following disclaimer in the documentation
--    and/or other materials provided with the distribution.
-- 
-- THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
-- ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
-- WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
-- DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
-- ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
-- (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
-- LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
-- ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
-- (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
-- SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
-- 
-- The views and conclusions contained in the software and documentation are those
-- of the authors and should not be interpreted as representing official policies,
-- either expressed or implied, of the FreeBSD Project.    
-- 
-- Version 1.0: Initial release
----------------------------------------------------------------------------------


-- CONFIGURABLE SCRIPT PARAMETERS
----------------------------------------------------------------------------------

-- Unique param table index
local PARAM_TABLE_KEY = 111
-- Parameter prefix
local PARAM_TABLE_PREFIX = "ESC_MAVS_"
-- Index of the serial port with enabled Lua support.
local SERIAL_PORT_NUMBER = 0
-- Offset of the ESC set, detected by this script possibly withan Expander 
local ESC_INDEX_OFFSET = 0


-- CONSTANTS
----------------------------------------------------------------------------------

local BUS_REQ_BROADCAST = 0x3E
local BUS_REQ_SINGLE = 0x3D
-- Maximum channels transmitted to attached device
local MAX_CHANNELS = 8

local DevCommand_Channels              = 0x31   -- Channels
local DevCommand_RecvTelemetry         = 0x3A   -- Telemetry request
local DevCommand_DetectRequestDirect   = 0x50 -- Device detect - direct request
local DevCommand_DetectRequestResponse = 0x40 -- Device detect
local DevCommand_SpecialCmd            = 0x70   -- Special command (Command - value)
local DevCommand_SpecialCmdTemp        = 0x71   -- Special command - motor temperature
  
-- Command identifier (SpecialCmd) 
local Cmd_Esc_SetPWM            = 0x10   -- ESC Command
local Cmd_Stg_SetThrottle       = 0x30   -- Starter-generator command


local MAV_SEVERITY = {EMERGENCY=0, ALERT=1, CRITICAL=2, ERROR=3, WARNING=4, NOTICE=5, INFO=6, DEBUG=7}
--Serial port identifier
local port = nil

-- Message identifier
local msgCnt = 0
-- List of detected devices
local exDevices = {}
-- List of explored devices
local exExploredDevices = {}
-- Number of escs
local devicesDetected = 0
-- MAVLINK telemetry
local telem_data = ESCTelemetryData()
-- Autodetection counter
local autodetectCounter = -100


-- bind a parameter to a variable given
local function bind_param(name)
    local p = Parameter()
    assert(p:init(name), string.format('ESC_MAVS: Parameter %s not found', name))
    return p
end

-- add a parameter and bind it to a variable
local function bind_add_param(name, idx, default_value)
    assert(param:add_param(PARAM_TABLE_KEY, idx, name, default_value), string.format('ESC_MAVS: Could not add param %s', name))
    return bind_param(PARAM_TABLE_PREFIX .. name)
end

-- setup script specific parameters
assert(param:add_table(PARAM_TABLE_KEY, PARAM_TABLE_PREFIX, 4), 'ESC_MAVS: Could not add param table')

--[[
  // @Param: ESC_MAVS_ENABLE
  // @DisplayName: MAV Sense ESC Enable
  // @Description: Enable ESC telemetry
  // @Values: 0:Disabled,1:Enabled
  // @User: Standard
--]]
ESC_MAVS_ENABLE = bind_add_param("ENABLE", 1, 0)


----------------------------------------------------------------------------------
-- CRC16 calculation
----------------------------------------------------------------------------------
local CRC16Lookup = {
	0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf, 
  0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
  0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e, 
  0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876, 
  0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd, 
  0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5, 
  0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c, 
  0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974, 
  0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb, 
  0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3, 
  0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a, 
  0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72, 
  0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9, 
  0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1, 
  0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738, 
  0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70, 
  0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7, 
  0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff, 
  0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036, 
  0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e, 
  0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5, 
  0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd, 
  0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134, 
  0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c, 
  0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3, 
  0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb, 
  0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232, 
  0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a, 
  0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1, 
  0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9, 
  0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330, 
  0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78 
}

 
local function crc16_array(bytes)
	local crc = 0
	for i=1,#bytes do
		local b = bytes[i]
		crc = ((crc>>8) & 0xffff) ~ CRC16Lookup[(((crc)~b) & 0xff) + 1]
	end
    return crc
end


----------------------------------------------------------------------------------
-- Serial port operations
----------------------------------------------------------------------------------
local function read_bytes(n)
   local ret = {}
   for i = 1, n do
      ret[i] = port:read()
   end
   return ret
end

local function write_bytes(buffer) 
  --[[local result = table.concat(
    -- Map each number to its corresponding character
    (function()
        local chars = {}
        for _, num in ipairs(buffer) do
            table.insert(chars, string.char(num))
        end
        return chars
    end)()
  )
  port:writestring("test") ]]

  for i = 1, #buffer do
    port:write(buffer[i])
    --  if port:write(buffer[i]) ~= 1 then
    --    return false
    --  end
  end
  return true 
end

----------------------------------------------------------------------------------
-- discard pending bytes
----------------------------------------------------------------------------------
local function discard_pending()
   local n = port:available():toint()
   for _ = 1, n do
      port:read()
   end
end



----------------------------------------------------------------------------------
--  Serial data Command function for devices that support it
-- cmd = Cmd_Stg_SetThrottle - a command for a starter-generator, to set thr. position
-- value - -8191 ... 0 ... 8191 - channel value, represents 1.0 ... 1.5 ... 2.0ms
----------------------------------------------------------------------------------
local function telemetryCommandSpecial(cmd, value)
  local outputBuffer = {}
  outputBuffer[1] = BUS_REQ_BROADCAST  -- preamb 1
  outputBuffer[2] = 0x03  -- preamb 2 = zakaz
  outputBuffer[3] = 12  -- Length
  outputBuffer[4] = msgCnt
  msgCnt = (msgCnt + 1) & 0xFF  -- Increment with wrap-around
  outputBuffer[5] = DevCommand_SpecialCmd
  outputBuffer[6] = 4  -- Sublen = 4

  -- Write the int16_t values (Cmd_Stg_SetThrottle and value)
  outputBuffer[7] = cmd & 0xFF
  outputBuffer[8] = (cmd >> 8) & 0xFF
  outputBuffer[9] = value & 0xFF
  outputBuffer[10] = (value >> 8) & 0xFF

  -- Calculate CRC for the first 10 bytes
  local crc = crc16_array(outputBuffer)
  outputBuffer[11] = crc & 0xFF
  outputBuffer[12] = (crc >> 8) & 0xFF

  -- Return the total message length
  return outputBuffer
end


----------------------------------------------------------------------------------
-- Request a complex telemetry (non-standard EX Bus format) from the device
----------------------------------------------------------------------------------
local function telemetryReqBusComplex()
  local outputBuffer = {}
  outputBuffer[1] = BUS_REQ_SINGLE  -- preamb 1
  outputBuffer[2] = 0x01  -- preamb 2 = always wait for response
  outputBuffer[3] = 9  -- Length
  outputBuffer[4] = msgCnt
  msgCnt = (msgCnt + 1) & 0xFF  -- Increment with wrap-around
  outputBuffer[5] = DevCommand_RecvTelemetry
  outputBuffer[6] = 1  -- Sublen = 1
  outputBuffer[7] = 0x01  -- Value 1 = activate complex telemetry

  -- Calculate CRC for the first 7 bytes
  local crc = crc16_array(outputBuffer)
  outputBuffer[8] = crc & 0xFF
  outputBuffer[9] = (crc >> 8) & 0xFF

  -- Return the total message length
  return outputBuffer
end



----------------------------------------------------------------------------------
-- Request a device info
----------------------------------------------------------------------------------
local function telemetryReqDeviceDetect()
  local outputBuffer = {}
  if #exExploredDevices > 0 then
    -- Remove the first item from index
    table.remove(exExploredDevices,1)
  end
  
  if #exExploredDevices == 0 then
    -- Fill the explored devices from the device table
    exExploredDevices[#exExploredDevices+1] = {} -- Fill empty parrent
    for id,dev in pairs(exDevices) do
      
      for j = 1, dev.extOutputs do
        exExploredDevices[#exExploredDevices+1] = { parent = dev, parentId = id, extOutput = j }
      end 
    end
  end
  
  local exploredDevice = exExploredDevices[1]
  --Set general explore command if we do not know the parrent device
  if not exploredDevice or not exploredDevice.parent then
    outputBuffer[1] = BUS_REQ_SINGLE  -- preamb 1
    outputBuffer[2] = 0x01  -- preamb 2 = always wait for response
    outputBuffer[3] = 8  -- Length
    outputBuffer[4] = msgCnt
    msgCnt = (msgCnt + 1) & 0xFF  -- Increment with wrap-around
    outputBuffer[5] = DevCommand_DetectRequestResponse
    outputBuffer[6] = 0  -- Sublen = 1
     

    -- Calculate CRC for the first 7 bytes
    local crc = crc16_array(outputBuffer)
    outputBuffer[7] = crc & 0xFF
    outputBuffer[8] = (crc >> 8) & 0xFF
  else
    -- We know the parent device - send as subcommand
    outputBuffer[1] = DevCommand_DetectRequestDirect
    outputBuffer[2] = 5  -- Sublen = 5
    outputBuffer[3] = exploredDevice.parent.idHi & 0xFF
    outputBuffer[4] = (exploredDevice.parent.idHi>>8) & 0xFF
    outputBuffer[5] = exploredDevice.parent.idLo & 0xFF
    outputBuffer[6] = (exploredDevice.parent.idLo>>8) & 0xFF
    outputBuffer[7] = exploredDevice.extOutput 
  end

  -- Return the total message length
  return outputBuffer
end
 

----------------------------------------------------------------------------------
-- Transmit the channel values to the device
-- channels: an array containing up to MAX_CHANNELS values ranging from -6000 to 6000
--           That corresponds to 1.50ms +/- 750us
-- expectReply: true if we expect any device to reply, false if the message is followed 
--           by another transmitted message.
-- additionalData: To be appended after channel values
----------------------------------------------------------------------------------
local function dataSendBus(channels, expectReply, additionalData)
  local outputBuffer = {}
  outputBuffer[1] = BUS_REQ_BROADCAST
  outputBuffer[2] = expectReply and 0x01 or 0x03
  outputBuffer[3] = 0  -- Length
  outputBuffer[4] = msgCnt
  msgCnt = (msgCnt + 1) & 0xFF  -- Increment with wrap-around
  outputBuffer[5] = DevCommand_Channels
  outputBuffer[6] = MAX_CHANNELS*2  
  local ch = 0
  for i=1,MAX_CHANNELS do
    ch = 12000 -- Channel midpoint (1.5ms)
    if i <= #channels then 
      ch = ch + channels[i]
    end
    outputBuffer[#outputBuffer+1] = ch & 0xFF
    outputBuffer[#outputBuffer+1] = (ch>>8) & 0xFF
    
  end
  if additionalData then
    for i, b in ipairs(additionalData) do
        table.insert(outputBuffer, b)
    end
  end
  
     
   
  -- Calculate CRC for the first N bytes
  outputBuffer[3] = #outputBuffer+2
  local crc = crc16_array(outputBuffer)
  outputBuffer[#outputBuffer+1] = crc & 0xFF
  outputBuffer[#outputBuffer+1] = (crc >> 8) & 0xFF
  
  -- Return the total message length
  return outputBuffer
end


-- Telemetry data read variables
local dataReadBuffer = {}
local STATE = {IDLE = 0, BUS = 1, BUSLEN = 2, BUSBODY = 3}
local dataReadState = STATE.IDLE

-- Number of remaining bytes in the message
local dataReadRemains = 0

-- Flag that we are reading echo from half duplex uart
local dataReadEcho = false  

----------------------------------------------------------------------------------
-- Clear the receiving telemetry buffer
----------------------------------------------------------------------------------
local function dataClearBuffer()
  dataReadRemains = 0
  dataReadState = STATE.IDLE
end

----------------------------------------------------------------------------------
-- Parse the incoming messages from UART
----------------------------------------------------------------------------------
local function dataCheckBusReply()
  local c
  
  while true do
    c = port:read() 
    if c < 0 then break end
    if dataReadState == STATE.IDLE then 
      if c == 0x3D or c == 0x3E then
        dataReadBuffer = {}
        dataReadBuffer[#dataReadBuffer+1] = c
        dataReadState = STATE.BUS
        dataReadEcho = true -- ECHO is skipped
      end    
      if c == 0x3B or c == 0x3C then
        dataReadBuffer = {}
        dataReadBuffer[#dataReadBuffer+1] = c
        dataReadState = STATE.BUS
        dataReadEcho = false
      end    
    elseif dataReadState == STATE.BUS then
      dataReadBuffer[#dataReadBuffer+1] = c
      if c > 3 then dataReadState = STATE.IDLE else  dataReadState = STATE.BUSLEN end
    elseif dataReadState == STATE.BUSLEN then
      dataReadBuffer[#dataReadBuffer+1] = c
      dataReadRemains = c-3
      dataReadState = STATE.BUSBODY
    elseif dataReadState == STATE.BUSBODY then
      dataReadBuffer[#dataReadBuffer+1] = c
      dataReadRemains = dataReadRemains - 1
      if dataReadRemains <= 0 then 
        -- Found the complete buffer
        dataReadState = STATE.IDLE
        local crc = crc16_array(dataReadBuffer)
        if crc ~= 0 then 
          gcs:send_text(MAV_SEVERITY.WARNING, "ESC_MAVS: CRC error.")
        elseif not dataReadEcho then
          return dataReadBuffer
        end   
      end
    end
  end
  return false
end


----------------------------------------------------------------------------------
-- Parse telemetry
----------------------------------------------------------------------------------
local function parseTelemetry(packet)
  if #packet < 12 then return end
  local identifier = packet[5]
  local sublen = packet[6]
  local idHi = 0
  local idLo = 0
  if identifier == DevCommand_RecvTelemetry then
    -- Telemetry - EX telemetrie from index 7 
    -- 
    local exlen = packet[8] & 0x3F
    local exType = (packet[8] >> 6) & 0x03
    if (packet[7] & 0x0F) == 0x0F then 
      idHi = packet[9] | (packet[10] << 8)
      idLo = packet[11] | (packet[12] << 8)
      --local deviceId = string.format("%i:%i",idHi, idLo)
      local deviceId = (idHi << 16) | idLo
      
      if exType == 3 and exDevices[deviceId] then
        --EX Type - complex telemetry
        if packet[14] == 0x04 then -- ESC telemetry
          local dev = exDevices[deviceId]
          dev.status = packet[15]
          dev.voltage = packet[16] | (packet[17]<<8) --X.XXV
          dev.current = packet[18] | (packet[19]<<8) --X.XXA
          dev.capacity = packet[20] | (packet[21]<<8) | (packet[22]<<16) | (packet[23]<<24)--XmAh
          dev.pwm = packet[24] | (packet[25]<<8) --X%
          dev.rpm = packet[26] | (packet[27]<<8) --X RPM
          dev.power = packet[28] | (packet[29]<<8) | (packet[30]<<16) | (packet[31]<<24) --X Watt
          --Show telemetry on GCS
          --gcs:send_text(MAV_SEVERITY.INFO, string.format("ESC_MAVS: Telemetry %iV, %iA, %imAh, %iPWM, %iW, %iRPM",dev.voltage,dev.current,dev.capacity,dev.pwm,dev.power,dev.rpm))
          if dev["runtime"] then return dev end
        elseif packet[14] == 0x05 then -- AUX ESC telemetry
          local dev = exDevices[deviceId]
          dev.status = packet[15]
          dev.runtime = packet[16] | (packet[17]<<8) | (packet[18]<<16) | (packet[19]<<24)--X s
          dev.temp = packet[20] | (packet[21]<<8) --X °C
          dev.motorTemp = packet[22] | (packet[23]<<8) --X °C
          dev.voltageBec = packet[24] | (packet[25]<<8) --X.XXV
          dev.currentBec = packet[26] | (packet[27]<<8) --X.XXA
          --Show telemetry on GCS
          --gcs:send_text(MAV_SEVERITY.INFO, string.format("ESC_MAVS: Telemetry %is, %i°C, %i°CM, %iVbec, %iAbec",dev.runtime,dev.temp,dev.motorTemp,dev.voltageBec,dev.currentBec))
          if dev["voltage"] then return dev end
        end
       
      end
      
    end
    
  elseif identifier == DevCommand_DetectRequestResponse then
    -- Device identified itself
    idHi = packet[7] | (packet[8] << 8)
    idLo = packet[9] | (packet[10] << 8)
    local deviceId = (idHi << 16) | idLo
    if not exDevices[deviceId] then
      --Add device into a list
      local exploredDevice = exExploredDevices[1]
      local hwId = packet[11] | (packet[12] << 8)
      local protocol = packet[13]
      local extOutputs = packet[14]
      local name = string.char(table.unpack(packet,15,26))
      name = name:gsub("[^%w%-%_]", "")
      local swL = packet[27]
      local swH = packet[28]
      local features = packet[29] 
      local parentSlot
      if exploredDevice and exploredDevice.extOutput then
        local se4Table = {3,0,1,2}
        if exploredDevice.parent.hwId == 0xEA8A then --SE4
          parentSlot=se4Table[exploredDevice.extOutput]
        else
          parentSlot=exploredDevice.extOutput-1 --slot from zero
        end
        -- gcs:send_text(MAV_SEVERITY.INFO, string.format("Device parent:  HW %X, %s, slot %i",exploredDevice.parent.hwId,exploredDevice.parent.name, exploredDevice.extOutput))
      end
      
      exDevices[deviceId] = {
        index = devicesDetected,
        parent = exploredDevice and exploredDevice.parentId or nil,
        parentSlot = parentSlot,
        idHi = idHi,
        idLo = idLo,
        hwId = hwId,
        extOutputs = extOutputs,
        name = name,
        sw = swH + swL * 0.01
      }
      devicesDetected = devicesDetected + 1
      gcs:send_text(MAV_SEVERITY.INFO, string.format("Device added: %s V%.2f ID%05i:%05i, slot %i",name,swH + swL * 0.01, idHi, idLo, exDevices[deviceId].parentSlot or -1))
    end
      
    
  end
  return false
end




local function checkBus()
  -- Channel range within +/- 4000 from center 
  -- Center = 12000 ~ 1.5ms. 
  -- Minimum = 8000 ~ 1.0ms
  -- Maximum = 16000 ~ 2.0ms
  local channel1 = 3000
  local channel2 = -3000
  
  local reply = dataCheckBusReply()
  if reply then
    -- Check data from telemetry - reply received
    local dev = parseTelemetry(reply)
    
    if dev and dev["voltage"] then
      --Process telemetry
      telem_data:voltage(dev.voltage * 0.01)
      telem_data:current(dev.current * 0.01)
      telem_data:temperature_cdeg(dev.temp*100)
      telem_data:motor_temp_cdeg(dev.motorTemp*100)
      telem_data:consumption_mah(dev.capacity)
      local escIndex = (dev.parentSlot or dev.index) + ESC_INDEX_OFFSET
      esc_telem:update_rpm(escIndex, dev.rpm, 0)
         -- 0x1F is temperature + voltage + current + motor temp + capacity
      esc_telem:update_telem_data(escIndex, telem_data, 0x1F)
      
      -- care must be taken when selecting a name, must be less than four characters and not clash with an existing log type
      -- format characters specify the type of variable to be logged, see AP_Logger/README.md
      -- https://github.com/ArduPilot/ardupilot/tree/master/libraries/AP_Logger
      -- not all format types are supported by scripting only: i, L, e, f, n, M, B, I, E, and N
      -- lua automatically adds a timestamp in micro seconds
      -- logger.write('MAVS','I,PNum,RPM,Curr,Volt,InT,OutT,PCurr,MosT,CapT,Status',
      --                'BHHfffffBBH', '#-qAv--AOO-', '--00000000-',
      --                ofs+i, pnum, RPM, curr, volt, in_thr, out_thr, pcurr, mos_temp, cap_temp, status)
                    
    end
    --gcs:send_text(MAV_SEVERITY.ALERT, "ESC_MAVS: Packet ok")
  end
  dataClearBuffer()
  
  -- Telemetry request prepare
  local autoDetectBuffer
  autodetectCounter = autodetectCounter + 1
  if autodetectCounter > 50 then autodetectCounter = 0 end
  if autodetectCounter <= 0 then
    -- Detect a device on the bus, do not send telemetry request. 
    -- This packet is send 100x after device startup
    autoDetectBuffer = telemetryReqDeviceDetect()
     
  end
  
  local buffer
  local channels = {channel1,channel2}
  local expectReply = false
  -- Send channels followed by a telemetry request
  if autoDetectBuffer and autoDetectBuffer[1]==DevCommand_DetectRequestDirect then
    expectReply = true
    buffer = dataSendBus(channels, expectReply, autoDetectBuffer)
    autoDetectBuffer = nil
  else
    buffer = dataSendBus(channels, expectReply)
  end
  
   
  if not write_bytes(buffer) then 
    gcs:send_text(MAV_SEVERITY.ERROR, "ESC_MAVS: serial write failed (full buffer?)")
    return 
  end
  
  if not expectReply then
    if autoDetectBuffer then
      if not write_bytes(autoDetectBuffer) then 
        gcs:send_text(MAV_SEVERITY.ERROR, "ESC_MAVS: serial write failed (full buffer?)")
        return 
      end
    else
      -- Request telemetry if not detecting a device
      buffer = telemetryReqBusComplex()
      if not write_bytes(buffer) then 
        gcs:send_text(MAV_SEVERITY.ERROR, "ESC_MAVS: serial write failed (full buffer?)")
        return 
      end
    end
  end 
  
end










if ESC_MAVS_ENABLE:get() ~= 1 then
  gcs:send_text(MAV_SEVERITY.INFO, "ESC_MAVS: Disabled.")
  return
end



-- find the serial first (or Nth) scripting serial port instance
port = serial:find_serial(SERIAL_PORT_NUMBER)

if not port then
    gcs:send_text(MAV_SEVERITY.ERROR, "ESC_MAVS: No scripting serial port.")
    return
end

-- begin the serial port
port:begin(125000)
port:set_flow_control(0)

 
 



-- the main update function that is used to read in data from serial port
function update()

    checkBus() 
--[[
    local n_bytes = port:available()
    while n_bytes > 0 do
        local byte = port:read()
        if decode(byte) then
            -- we have got a full line
            -- save to data flash

            -- care must be taken when selecting a name, must be less than four characters and not clash with an existing log type
            -- format characters specify the type of variable to be logged, see AP_Logger/README.md
            -- not all format types are supported by scripting only: i, L, e, f, n, M, B, I, E, N, and Z
            -- Note that Lua automatically adds a timestamp in micro seconds
            logger:write('SCR','Sensor1,Sensor2,Sensor3','fff',table.unpack(log_data))

            -- reset for the next message
            log_data = {}
        end
        n_bytes = n_bytes - 1
    end
]]
    return update, 20
end

gcs:send_text(MAV_SEVERITY.ALERT, "ESC_MAVS: Driver loaded")

return update, 100