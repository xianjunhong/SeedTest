class TestUtils:
    def test_get_file_name(self):
        """
        Test get_file_name function
        """
        print("Testing get_file_name function...")

    def quick_sort(self, arr):
        """
        Quick sort function
        """
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return self.quick_sort(left) + middle + self.quick_sort(right)
    def test_quick_sort(self):
        """
        Test quick_sort function
        """
        print("Testing quick_sort function...")
        arr = [3, 6, 8, 10, 1, 2, 4, 5, 7, 9]
        sorted_arr = self.quick_sort(arr)
        print(f"Sorted array: {sorted_arr}")

