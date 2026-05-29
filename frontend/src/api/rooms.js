import api from './client'

export const roomsApi = {
  getRoom(roomId) {
    return api.get(`/rooms/${roomId}`)
  },

  createRoom(name) {
    return api.post('/rooms/', { name })
  },

  joinRoom(inviteCode) {
    return api.post('/rooms/join', { invite_code: inviteCode })
  },

  finishRoom(roomId) {
    return api.post(`/rooms/${roomId}/finish`)
  },

  getBalances(roomId) {
    return api.get(`/rooms/${roomId}/balances`)
  },

  getSettlements(roomId) {
    return api.get(`/rooms/${roomId}/settlements`)
  },

  generateRoute(roomId, { budget, radiusKm, latitude, longitude }) {
    return api.post(`/rooms/${roomId}/route`, {
      budget,
      radius_km: radiusKm,
      latitude,
      longitude,
    })
  },
}