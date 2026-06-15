/**
 * @file API layer managing spaces, shared budget parameters, settlement accounting, and maps routing.
 */

import api from './client'

/**
 * Endpoint configurations dealing with spatial calculation spaces.
 * @namespace roomsApi
 */
export const roomsApi = {
  /**
   * Pulls structural entries list outlining all rooms connected to current active user profile.
   * @memberof roomsApi
   * @returns {Promise<AxiosResponse<any>>}
   */
  getMyRooms() {
    return api.get('/rooms/my')
  },

  /**
   * Captures targeted single internal setup object outlining specialized configurations of one space.
   * @memberof roomsApi
   * @param {string|number} roomId - Unique identification string index value.
   * @returns {Promise<AxiosResponse<any>>}
   */
  getRoom(roomId) {
    return api.get(`/rooms/${roomId}`)
  },

  /**
   * Spawns a newly created group billing session workspace container node.
   * @memberof roomsApi
   * @param {string} name - Explicit title tag representing text header identifying the room.
   * @returns {Promise<AxiosResponse<any>>}
   */
  createRoom(name) {
    return api.post('/rooms/', { name })
  },

  /**
   * Attempts authentication profile linkage access using invitation shortcode strings.
   * @memberof roomsApi
   * @param {string} inviteCode - Alphanumeric pass-phrase identifier enabling user profile entry access.
   * @returns {Promise<AxiosResponse<any>>}
   */
  joinRoom(inviteCode) {
    return api.post('/rooms/join', { invite_code: inviteCode })
  },

  /**
   * Freezes a workspace room from receiving modifications or subsequent invoice uploads.
   * @memberof roomsApi
   * @param {string|number} roomId - Unique reference ID identifier.
   * @returns {Promise<AxiosResponse<any>>}
   */
  finishRoom(roomId) {
    return api.post(`/rooms/${roomId}/finish`)
  },

  /**
   * Processes a real-time list evaluating individual financial status sheets.
   * @memberof roomsApi
   * @param {string|number} roomId - Target tracking session identity pointer index value.
   * @returns {Promise<AxiosResponse<any>>}
   */
  getBalances(roomId) {
    return api.get(`/rooms/${roomId}/balances`)
  },

  /**
   * Generates calculated payment instructions to optimize debt settlement between group members.
   * @memberof roomsApi
   * @param {string|number} roomId - Core location tracker identity mapping identifier.
   * @returns {Promise<AxiosResponse<any>>}
   */
  getSettlements(roomId) {
    return api.get(`/rooms/${roomId}/settlements`)
  },

  /**
   * Coordinates travel route calculation processing inside explicit geographical radius constraints.
   * @memberof roomsApi
   * @param {string|number} roomId - Core primary key reference string.
   * @param {Object} parameters - Structural limits filtering tracking point calculations.
   * @param {number} parameters.budget - High-level target limit numerical boundary index constraint value.
   * @param {number} parameters.radiusKm - Spherical search extent radius specified in kilometers.
   * @param {number} parameters.latitude - GPS standard coordinate center base location latitude data point.
   * @param {number} parameters.longitude - GPS standard coordinate center base location longitude data point.
   * @returns {Promise<AxiosResponse<any>>}
   */
  generateRoute(roomId, { budget, radiusKm, latitude, longitude }) {
    return api.post(`/rooms/${roomId}/route`, {
      budget,
      radius_km: radiusKm,
      latitude,
      longitude,
    })
  },

  /**
   * Gathers coordinate target candidates scattered around specified geolocation map pins.
   * @memberof roomsApi
   * @param {string|number} roomId - Target context room identifier.
   * @param {Object} geolocation - Target anchor geographical metrics mapping payload block.
   * @param {number} geolocation.lat - Decimal tracking coordinate pinpoint latitude marker.
   * @param {number} geolocation.lon - Decimal tracking coordinate pinpoint longitude marker.
   * @param {number} geolocation.radiusKm - Search constraint bounds set in metric kilometers.
   * @returns {Promise<AxiosResponse<any>>}
   */
  getRouteCandidates(roomId, { lat, lon, radiusKm }) {
    return api.post(`/rooms/${roomId}/route-candidates?lat=${lat}&lon=${lon}&radius_km=${radiusKm}`)
  },

  /**
   * Saves the generated path blueprint asset mapping coordinates to a specific room configuration profile.
   * @memberof roomsApi
   * @param {string|number} roomId - Core root identification space data tracker string index location.
   * @param {Object} payload - Complete collection data mapping selected path sequences.
   * @returns {Promise<AxiosResponse<any>>}
   */
  saveRoute(roomId, payload) {
    return api.post(`/rooms/${roomId}/save-route`, payload)
  },
}