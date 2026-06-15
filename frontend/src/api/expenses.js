/**
 * @file API context mapping management endpoints processing application room split-billing expenses.
 */

import api from './client'

/**
 * Methods for managing room-specific transaction split expenses.
 * @namespace expensesApi
 */
export const expensesApi = {
  /**
   * Fetches an index listing of expenses logged inside an absolute room boundary space.
   * * @memberof expensesApi
   * @param {string|number} roomId - The room primary identification identifier.
   * @returns {Promise<AxiosResponse<any>>}
   */
  getExpenses(roomId) {
    return api.get(`/expenses/${roomId}`)
  },

  /**
   * Registers a bill entry item to be divided proportionally within group space members.
   * * @memberof expensesApi
   * @param {Object} expenseDetails - Details describing individual purchase allocation layout.
   * @param {string|number} expenseDetails.roomId - Shared workspace space key link assignment.
   * @param {string|number} expenseDetails.payerId - Unique ID of the profile user lodging standard coverage payment.
   * @param {number} expenseDetails.amount - Total numerical value assigned to item checkout expense total.
   * @param {string} expenseDetails.description - Text context summary summarizing purchase reasons.
   * @param {Array<number>} expenseDetails.splitBetween - Array collection listing user profile elements splitting bills.
   * @returns {Promise<AxiosResponse<any>>}
   */
  createExpense({ roomId, payerId, amount, description, splitBetween }) {
    return api.post('/expenses/', {
      room_id: roomId,
      payer_id: payerId,
      amount,
      description,
      split_between: splitBetween,
    })
  },

  /**
   * Destroys a tracked billing element targeting its specific primary database id.
   * * @memberof expensesApi
   * @param {string|number} id - Target identification entity row location data string.
   * @returns {Promise<AxiosResponse<any>>}
   */
 deleteExpense(id) {
    return api.delete(`/expenses/${id}`)
  },
}