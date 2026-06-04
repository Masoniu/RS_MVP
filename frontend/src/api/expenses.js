import api from './client'

export const expensesApi = {
  getExpenses(roomId) {
    return api.get(`/expenses/${roomId}`)
  },

  createExpense({ roomId, payerId, amount, description, splitBetween }) {
    return api.post('/expenses/', {
      room_id: roomId,
      payer_id: payerId,
      amount,
      description,
      split_between: splitBetween,
    })
  },

 deleteExpense(id) {
    return api.delete(`/expenses/${id}`)
  },
}